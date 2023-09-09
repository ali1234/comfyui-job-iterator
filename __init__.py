NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def register_node(c):
    assert not isinstance(c.RETURN_TYPES, str), "Error: string found instead of tuple."
    assert not isinstance(c.RETURN_NAMES, str), "Error: string found instead of tuple."
    NODE_CLASS_MAPPINGS[c.__name__] = c
    NODE_DISPLAY_NAME_MAPPINGS[c.__name__] = c.__name__
    return c


from . import sequence, paths, job, misc



