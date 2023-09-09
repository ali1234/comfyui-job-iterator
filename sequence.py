import ast
import functools
import itertools

from . import register_node


# Sequence creation.


@register_node
class Range:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start": ("INT", {"default": 0, "min": 0, "max": 9999999, "step": 1}),
                "stop": ("INT", {"default": 0, "min": 0, "max": 9999999, "step": 1}),
                "step": ("INT", {"default": 0, "min": 0, "max": 9999999, "step": 1}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/sequence"

    def go(self, start, stop, step):
        return (range(start, stop, step), )


@register_node
class Literal:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "literal": ("STRING", {'default': '', 'multiline': True})
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/sequence"

    def go(self, literal):
        return (ast.literal_eval(literal), )


# Processing of existing sequences.


@register_node
class Reorder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sequence": ("SEQUENCE", ),
                "method": (("reverse", "sort", "reverse sort"), {"default": "sort"}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/sequence"

    def go(self, sequence, method):
        f = {"reverse": reversed, "sort": sorted, "reverse_sort": lambda x: sorted(x, reverse=True)}[method]
        return (f(sequence), )


@register_node
class Combinations:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sequence": ("SEQUENCE", ),
                "count": ("INT", {"default": 0, "min": 0, "max": 9999999, "step": 1}),
                "replacement": ("BOOLEAN", {"default": False, "label_on": "Yes", "label_off": "No"}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/sequence"

    def go(self, sequence, count, replacement):
        if replacement:
            return (itertools.combinations_with_replacement(sequence, count), )
        else:
            return (itertools.combinations(sequence, count), )


@register_node
class Permutations:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sequence": ("SEQUENCE", ),
                "count": ("INT", {"default": 0, "min": 0, "max": 9999999, "step": 1}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/attributes/combinatorics"

    def go(self, sequence, count):
        return ([x for x in itertools.permutations(sequence, count)], )


@register_node
class Join:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sequence": ("SEQUENCE", ),
                "join_str": ("STRING", {'default': ', '}),
            },
        }

    RETURN_TYPES = ("SEQUENCE", )
    RETURN_NAMES = ("sequence", )
    FUNCTION = "go"
    CATEGORY = "ali1234/attributes/combinatorics"

    def go(self, sequence, join_str):
        return ([join_str.join(x) for x in sequence], )
