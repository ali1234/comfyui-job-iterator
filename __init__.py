from typing_extensions import override

from comfy_api.latest import ComfyExtension, io

from .registry import set_pack_options, get_nodes

set_pack_options('jobiter', 'Job Iterator')

from . import nodes

class JobIterator(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return get_nodes()

async def comfy_entrypoint() -> JobIterator:  # ComfyUI calls this to load your extension and its nodes.
    return JobIterator()