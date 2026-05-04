import ast
import itertools
import torch

from ..registry import register_node
from ..types import *

# Sequence creation.

@register_node(category="Sequence")
def Range(start: Int() = 0, stop: Int() = 10, step: Int() = 1) -> (Sequence(), ):
        return range(start, stop, step),


@register_node(category="Sequence")
def Literal(literal: String(multiline = True) = "") -> (Any(), ):
    return ast.literal_eval(literal),


@register_node(category="Sequence")
def Combinatorics(sequence: Sequence(), min: Int() = 3, max: Int() = 4, replacement: Bool() = False, permutations: Bool() = False) -> (Sequence(), ):
    """Sequence combinatorics."""
    comb = itertools.combinations_with_replacement if replacement else itertools.combinations
    combs = itertools.chain(*(comb(sequence, n) for n in range(min, max+1)))
    if permutations:
        combs = itertools.chain(*(itertools.permutations(x) for x in combs))
    return list(combs),


reorder_modes = {'reverse': reversed, 'sort': sorted}

@register_node(category="Sequence")
def Reorder(sequence: Sequence(), mode: Combo(choices=reorder_modes) = 'reverse') -> (Sequence(), ):
    return list(mode(sequence)),


format_modes = {
    'mapping': lambda x, y: x.format(**y),
    'iterable': lambda x, y: x.format(*y),
    'single': lambda x, y: x.format(y)
}

@register_node(category="Text")
def Format(vars: Any(), string: String(multiline=True) = "", mode: Combo(choices=format_modes) = 'mapping') -> (String(), ):
    """Performs string replacement using the standard Python format() method."""
    return mode(string, vars),


@register_node(category="Text")
def Join(sequence: Sequence(), sep: String() = ", ") -> (String(), ):
    """Joins a sequence of strings into a single string."""
    return sep.join(str(x) for x in sequence),

@register_node(display_name="Join Tensor Sequence", category="Utils")
def JoinTensorSequence(sequence: Sequence(), dim: Int(min=0, max=10) = 0) -> (Any(), ):
    return torch.cat(sequence, dim=dim),


@register_node(display_name="Split Image Batch", category="Utils")
def SplitImageBatch(images: Image(), threshold: Float(min=0.001, max=1, step=0.001, round=0.001) = 0.01) -> (Sequence(), ):
    c = torch.argwhere(images.diff(dim=0).pow(2).mean(dim=(1, 2, 3)) > threshold).flatten() + 1
    print(c)
    last = 0
    output = []
    for frame in c:
        print(frame)
        output.append(images[last:frame])
        last = frame
    output.append(images[last:])
    return output,


@register_node(display_name="Mapped Join", category="Text")
def MappedJoin(sequence: Sequence(), sep: String() = ", ") -> (Sequence(), ):
    """Joins a sequence of iterables of strings into a sequence of single strings."""
    t = (sep.join(str(x) for x in s) for s in sequence)
    return list(t),


@register_node(display_name="Make Sequence")
def MakeSequence(items: AutogrowMatch(prefix='item', min=1)) -> (Sequence(), ):
    """Turns any inputs into a sequence."""
    return items,


@register_node(display_name="Get Item From Sequence", category="Sequence")
def GetFromSequence(sequence: MultiType(types=(Sequence(), Job())), index: Int() = 0) -> (Any(), ):
    """Gets the nth item from a sequence. Also works on jobs."""
    return sequence[index],
