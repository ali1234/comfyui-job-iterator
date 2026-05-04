import inspect
from functools import wraps

from comfy_api.latest import io

from .types import Autogrow, AutogrowMatch, Combo

PACK_BASE_CATEGORY = None
PACK_UID = None
PACK_NODES = []


def set_pack_options(uid: str, category: str = None):
    global PACK_BASE_CATEGORY, PACK_UID
    PACK_BASE_CATEGORY = category
    PACK_UID = uid


def make_category(category):
    cat_list = []
    if PACK_BASE_CATEGORY is not None:
        cat_list.append(PACK_BASE_CATEGORY)
    if category is not None:
        cat_list.append(category)
    return '/'.join(cat_list)


def make_unique_name(name, version=0):
    return f'{PACK_UID}_{version}_{name}'


def get_nodes():
    return PACK_NODES


def register_node_class(cls):
    PACK_NODES.append(cls)
    return cls


def register_node(category=None, version=0, display_name=None, output=False):
    def decorator(f):
        if PACK_UID is None:
            raise Exception("PACK_UID is not set. Call set_pack_options in __init__.py to set it.")

        unique_name = make_unique_name(f.__name__, version)

        sig = inspect.signature(f)
        node_attrs = {}

        final_category = make_category(category)
        if not final_category:
            print(f"WARNING: No category specified for {f.__name__} and no base category. It won't be shown in menus.")

        def define_schema(cls) -> io.Schema:
            return io.Schema(
                node_id=unique_name,
                display_name=display_name or f.__name__,
                category=final_category,
                inputs=list(v.annotation.Input(k, v.default) for k, v in sig.parameters.items()),
                outputs=list(v.Output() for v in sig.return_annotation),
            )

        node_attrs['define_schema'] = classmethod(define_schema)

        def execute(cls, **kwargs) -> io.NodeOutput:
            for k, v in sig.parameters.items():
                if isinstance(v.annotation, Combo):
                    kwargs[k] = v.annotation[kwargs[k]]
                elif isinstance(v.annotation, Autogrow) or isinstance(v.annotation, AutogrowMatch):
                    kwargs[k] = list(kwargs[k].values())
            return io.NodeOutput(*f(**kwargs))

        node_attrs['execute'] = classmethod(execute)

        node_class = type(unique_name, (io.ComfyNode,), node_attrs)
        PACK_NODES.append(node_class)
        return node_class

    return decorator
