"""
Generic sequence looping via ComfyUI graph expansion (expand), supporting:
- multiple independent loops in one workflow
- nested loops
- accumulation driven ONLY by LoopEnd.value (always collects; if value unconnected -> None)
- strict "loop region" definition by forward reachability from the LoopStart
- validation: no edges may "escape" the loop body to outside nodes except from
  the LoopEnd node itself (enables safe nesting and composition)

UX / wiring:
- Users wire the upstream sequence ONLY into LoopStart.
- Between LoopStart and LoopEnd there are only TWO wires:
    1) flow  (raw_link pairing, used for region discovery / nesting)
    2) data  (loop-carried state dict: index, accum, sequence)

Important implementation detail:
- The expanded clone must NOT rely on preserving external links as raw tuples.
  Therefore LoopStart stores the upstream sequence in `data["seq"]`, and LoopEnd
  reads it from there. This guarantees the recursive LoopEnd sees the real
  sequence via an internal connection (Start.data -> End.data) inside the loop.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, TypedDict

from comfy_api.latest import io

from comfy_execution.graph_utils import GraphBuilder, is_link

from ..types import *  # SequenceType, FlowType, etc.
from ..registry import register_node_class, make_unique_name, make_category


def _build_children_adjacency(prompt: Dict[str, Any]) -> Dict[str, List[str]]:
    """Build parent->children adjacency from prompt's input links."""
    children: Dict[str, List[str]] = {}
    for child_id, node in prompt.items():
        for _, v in node.get("inputs", {}).items():
            if is_link(v):
                parent_id = str(v[0])
                children.setdefault(parent_id, []).append(str(child_id))
    return children


def _reachable_region(children: Dict[str, List[str]], start_id: str, end_id: str) -> Set[str]:
    """Forward reachability from start_id, stopping recursion at end_id."""
    inside: Set[str] = set()
    stack: List[str] = [str(start_id)]
    while stack:
        nid = stack.pop()
        if nid in inside:
            continue
        inside.add(nid)
        if nid == str(end_id):
            continue
        for c in children.get(nid, []):
            stack.append(c)
    return inside


def _find_escape_edges(prompt: Dict[str, Any], inside: Set[str], end_id: str) -> List[Tuple[str, str, str]]:
    """
    Illegal edges are any inside->outside link, excluding those originating from end_id.
    Each entry: (parent_id, child_id, child_input_name)
    """
    escapes: List[Tuple[str, str, str]] = []
    end_id = str(end_id)

    for child_id, node in prompt.items():
        child_id = str(child_id)
        for input_name, v in node.get("inputs", {}).items():
            if not is_link(v):
                continue
            parent_id = str(v[0])
            if parent_id in inside and child_id not in inside and parent_id != end_id:
                escapes.append((parent_id, child_id, str(input_name)))

    return escapes


def _format_escape_error(escapes: List[Tuple[str, str, str]], start_id: str, end_id: str) -> str:
    lines = [
        "Loop body has illegal connections escaping to nodes outside the loop region.",
        f"LoopStart id: {start_id}",
        f"LoopEnd   id: {end_id}",
        "",
        "Illegal edges (producer -> consumer[input]):",
    ]
    for parent_id, child_id, input_name in escapes:
        lines.append(f"  - {parent_id} -> {child_id}[{input_name}]")
    lines += [
        "",
        "Fix: route values out of the loop via the LoopEnd node's outputs, or move the consumer node inside the loop.",
        "Note: outside->inside edges are allowed (loop-invariant dependencies).",
    ]
    return "\n".join(lines)


@register_node_class
class LoopStart(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id=make_unique_name(cls.__name__),
            display_name="Loop Start",
            category=make_category("Loop"),
            inputs=[
                io.MultiType.Input("sequence", types=[SequenceType, JobType]),
                SequenceType.Input("accum", optional=True),
                io.Int.Input("first_index", default=0),
            ],
            outputs=[
                FlowType.Output("flow"),
                SequenceType.Output("accum"),
                io.Int.Output("index"),
                io.AnyType.Output("item"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, sequence, accum=None, first_index=0):
        if accum is None:
            accum = []
        flow = {'sequence': sequence, 'index': first_index, 'accum': accum, 'start_id': cls.hidden.unique_id}
        return io.NodeOutput(flow, accum, first_index, sequence[first_index])


@register_node_class
class LoopEnd(io.ComfyNode):
    DISPLAY_NAME = "Loop End"
    CATEGORY = None

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id=make_unique_name(cls.__name__),
            display_name=cls.DISPLAY_NAME,
            category=make_category("Loop"),
            enable_expand=True,
            inputs=[
                FlowType.Input("flow"),
                io.AnyType.Input("result", optional=True),
                io.Combo.Input('mode', options=("append", "replace"), default="append")
            ],
            outputs=[
                SequenceType.Output("result"),
            ],
            hidden=[io.Hidden.dynprompt, io.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, flow, mode, result=None):
        flow = dict(flow)
        if mode == "append":
            flow['accum'] = flow['accum'] + [result]
        elif mode == "replace":
            flow['accum'] = result
        flow['index'] = flow['index'] + 1

        # Terminate: stop expanding.
        if flow['index'] >= len(flow['sequence']):
            return io.NodeOutput(flow['accum'])

        # Pairing: find connected start node id via flow
        start_id = flow['start_id']
        end_id = flow.setdefault('end_id', cls.hidden.unique_id)

        # Region discovery/validation on the ORIGINAL prompt graph
        prompt = flow.setdefault('prompt', cls.hidden.dynprompt.get_original_prompt())
        children = _build_children_adjacency(prompt)
        inside = _reachable_region(children, start_id=start_id, end_id=end_id)

        if end_id not in inside:
            raise RuntimeError(
                "LoopEnd is not reachable from LoopStart. "
                "Ensure your loop body connects from LoopStart outputs to LoopEnd inputs."
            )

        escapes = _find_escape_edges(prompt, inside=inside, end_id=end_id)
        if escapes:
            raise ValueError(_format_escape_error(escapes, start_id=start_id, end_id=end_id))

        graph = GraphBuilder()

        for node_id in inside:
            original_node = cls.hidden.dynprompt.get_node(node_id)
            class_type = original_node["class_type"]
            n = graph.node(class_type, node_id)
            n.set_override_display_id(node_id)

        # Wire inputs (internal links rewired to clones; external links/values kept as-is)
        for node_id in inside:
            original_node = cls.hidden.dynprompt.get_node(node_id)
            node = graph.lookup_node(node_id)

            for k, v in original_node.get("inputs", {}).items():
                if node_id != start_id:
                    if is_link(v) and v[0] in inside:
                        node.set_input(k, graph.lookup_node(v[0]).out(v[1]))
                    else:
                        node.set_input(k, v)

        new_start = graph.lookup_node(start_id)
        new_start.set_input("sequence", flow['sequence'])
        new_start.set_input("first_index", flow['index'])
        new_start.set_input("accum", flow['accum'])

        new_end = graph.lookup_node(end_id)
        new_end.set_input("flow", flow)

        return {
            "result": (new_end.out(0), ),  # results, data
            "expand": graph.finalize(),
        }
