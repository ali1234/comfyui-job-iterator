import typing, inspect

from pydantic import BaseModel

from comfy_api.latest import io


class ComfyType(BaseModel):
    TYPE: typing.ClassVar
    display_name: str = None
    optional: bool = None

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True)

    def Input(self, name, default=inspect._empty):
        if default is inspect._empty:
            return self.TYPE.Input(id=name, **self.opts())
        else:
            return self.TYPE.Input(id=name, default=default, **self.opts())

    def Output(self):
        return self.TYPE.Output()

class ComfyWidgetType(ComfyType):
    """Base type for ComfyUI types that have options controlling how they are displayed."""
    socketless: bool = None
    force_input: bool = None


class Int(ComfyWidgetType):
    TYPE = io.Int
    min: int = None
    max: int = None
    step: int = None
    display_mode: io.NumberDisplay = None


class Float(ComfyWidgetType):
    TYPE = io.Float
    min: float = None
    max: float = None
    step: float = None
    round: float = None
    display_mode: io.NumberDisplay = None


class String(ComfyWidgetType):
    TYPE = io.String
    multiline: bool = False


class Bool(ComfyWidgetType):
    TYPE = io.Boolean
    label_on: str = None
    label_off: str = None


class Image(ComfyWidgetType):
    TYPE = io.Image


class Video(ComfyWidgetType):
    TYPE = io.Video


class Combo(ComfyWidgetType):
    TYPE = io.Combo
    choices: typing.Mapping[str, typing.Any]

    def opts(self):
        return {
            'options': list(self.choices.keys()),
            **self.model_dump(mode='python', exclude_none=True, exclude={'choices'})
        }

    def Input(self, name, default=inspect._empty):
        if default is inspect._empty:
            return io.MultiType.Input(id=self.TYPE.Input(id=name, **self.opts()), types=(self.TYPE, io.String))
        else:
            return io.MultiType.Input(id=self.TYPE.Input(id=name, default=default, **self.opts()), types=(self.TYPE, io.String))

    def Output(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.choices[item]


class Any(ComfyType):
    TYPE = io.AnyType


SequenceType = io.Custom('SEQUENCE')
MappingType = io.Custom('MAPPING')
JobType = io.Custom('JOB')
FlowType = io.Custom('JOB_FLOW')


class Sequence(ComfyType):
    TYPE = SequenceType


class Mapping(ComfyType):
    TYPE = MappingType


class Job(ComfyType):
    TYPE = JobType


class Autogrow(ComfyType):
    TYPE = io.Autogrow
    input: ComfyType = Any()
    prefix: str = None
    min: int = None
    max: int = None

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True, exclude={'input', 'prefix', 'min', 'max', 'match'})

    def autoopts(self):
        return self.model_dump(mode='python', exclude_none=True, include={'prefix', 'min', 'max'})

    def Input(self, name, default):
        template = io.Autogrow.TemplatePrefix(self.input.Input(self.prefix), **self.autoopts())
        return self.TYPE.Input(name, template=template, **self.opts())

    def Output(self):
        raise NotImplementedError


class AutogrowMatch(ComfyType):
    TYPE = io.Autogrow
    prefix: str = None
    types: tuple = Any()
    min: int = None
    max: int = None

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True, exclude={'prefix', 'min', 'max', 'types'})

    def autoopts(self):
        return self.model_dump(mode='python', exclude_none=True, include={'prefix', 'min', 'max'})

    def Input(self, name, default):
        match_template = template_matchtype = io.MatchType.Template("type")
        template = io.Autogrow.TemplatePrefix(io.MatchType.Input(self.prefix, template=match_template), **self.autoopts())
        return self.TYPE.Input(name, template=template, **self.opts())

    def Output(self):
        raise NotImplementedError


class List(ComfyType):
    type: ComfyType = None

    def Output(self):
        return self.type.TYPE.Output(is_output_list=True)


class MultiType(ComfyType):
    TYPE = io.MultiType
    types: tuple = None

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True, exclude={'types'})

    def Input(self, name, default):
        return self.TYPE.Input(name, types=tuple(t.TYPE for t in self.types), **self.opts())

