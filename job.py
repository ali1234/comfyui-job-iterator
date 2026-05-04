import math

from .registry import register_node
from .types import *

class NamedSeq:
    def nth(self, n):
        raise NotImplementedError

    def __getitem__(self, n):
        return dict(self.nth(n))

class SingleSeq(NamedSeq):
    def __init__(self, name, seq):
        self._name = name
        self._seq = seq

    def nth(self, n):
        n = n % len(self)
        yield (self._name, self._seq[n])

    def __len__(self):
        return len(self._seq)


class CombinedSeq(NamedSeq):
    def __init__(self, *args):
        self._seqs = args


class ProductSeq(CombinedSeq):
    def nth(self, n):
        n = n % len(self)
        indices = []
        for s in reversed(self._seqs):
            indices.append(n % len(s))
            n //= len(s)

        for i, s in zip(reversed(indices), self._seqs):
            yield from s.nth(i)

    def __len__(self):
        return math.prod(len(s) for s in self._seqs)


class ZipSeq(CombinedSeq):
    def nth(self, n):
        n = n % len(self)
        for s in self._seqs:
            yield from s.nth(n)

    def __len__(self):
        return min(len(s) for s in self._seqs)


@register_node(display_name="Make Job")
def MakeJob(sequence: Sequence(), name: String() = "") -> (Job(), ):
    return SingleSeq(name, sequence),

combine_modes = {
    'zip': ZipSeq,
    'product': ProductSeq,
}

@register_node(display_name="Combine Jobs")
def CombineJobs(a: Job(), b: Job(), method: Combo(choices=combine_modes) = 'product') -> (Job(), ):
    return method(a, b),


@register_node(display_name="Enumerate Job")
def EnumerateJob(job: Job(), name: String() = "") -> (Job(), ):
    return ZipSeq(SingleSeq(name, range(len(job))), job),


@register_node(display_name="Get Job Step")
def GetJobStep(job: Job(), n: Int()=0) -> (JobStep(), ):
    return (job[n], )


@register_node(display_name="Get Step Attribute")
def GetStepAttribute(step: JobStep(), name: String() = "") -> (Any, ):
    return (step[name], )

