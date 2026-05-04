import ast
import itertools

from .registry import register_node
from .types import *

# Sequence creation.

@register_node()
def Range(start: Int() = 0, stop: Int() = 10, step: Int() = 1) -> (Sequence(), ):
        return (range(start, stop, step), )


@register_node()
def Literal(literal: String(multiline = True) = "") -> (Any, ):
    return (ast.literal_eval(literal), )




# Processing of existing sequences.

@register_node()
def Combinatorics(sequence: Sequence(), min: Int() = 3, max: Int() = 4, replacement: Bool() = False, permutations: Bool() = False) -> (Sequence(), ):
    """Sequence combinatorics."""
    comb = itertools.combinations_with_replacement if replacement else itertools.combinations
    combs = itertools.chain(*(comb(sequence, n) for n in range(min, max+1)))
    if permutations:
        combs = itertools.chain(*(itertools.permutations(x) for x in combs))
    return (list(combs), )

format_modes = {
    'mapping': lambda x, y: x.format(**y),
    'iterable': lambda x, y: x.format(*y),
    'single': lambda x, y: x.format(y)
}

@register_node()
def Format(vars: Any, string: String(multiline=True) = "", mode: Combo(choices=format_modes) = 'mapping') -> (String(), ):
    """Performs string replacement using the standard Python format() method."""
    return (mode(string, vars), )


@register_node()
def Join(sequence: Sequence(), sep: String() = ", ") -> (String(), ):
    """Joins an interable of strings into a single string."""
    return (sep.join(str(x) for x in sequence), )

@register_node(display_name="Mapped Join")
def MappedJoin(sequence: Sequence(), sep: String() = ", ") -> (Sequence(), ):
    """Joins a sequence of iterables of strings into a sequence of single strings."""
    t = (sep.join(str(x) for x in s) for s in sequence)
    return (list(t), )

@register_node(display_name="Make Sequence")
def MakeSequence(*inputs: Any) -> (Sequence(), ):
    """Collects variadic inputs into a single Sequence."""
    return (list(inputs), )


