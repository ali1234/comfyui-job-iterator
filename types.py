import typing

from pydantic import BaseModel


class ComfyWidgetType(BaseModel):
    """Base type for ComfyUI types that have options controlling how they are displayed."""
    TYPE: typing.ClassVar

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True)

    @property
    def type(self):
        return self.TYPE

    def __getitem__(self, item):
        return item


class Int(ComfyWidgetType):
    TYPE = 'INT'
    min: int = None
    max: int = None
    step: int = None
    display: typing.Literal["number", "slider"] = None


class Float(ComfyWidgetType):
    TYPE = 'FLOAT'
    min: float = None
    max: float = None
    step: float = None
    display: typing.Literal["number", "slider"] = None


class String(ComfyWidgetType):
    TYPE = 'STRING'
    multiline: bool = None


class Bool(ComfyWidgetType):
    TYPE = 'BOOLEAN'
    label_on: str = None
    label_off: str = None


class Color(ComfyWidgetType):
    """Widget only available if you have MTB node pack"""
    TYPE = 'COLOR'


class Combo(ComfyWidgetType):
    TYPE = 'COMBO'
    choices: typing.Mapping[str, typing.Any]

    def opts(self):
        return self.model_dump(mode='python', exclude_none=True, exclude={'choices'})

    @property
    def type(self):
        return list(self.choices.keys())

    def __getitem__(self, item):
        return self.choices[item]

# custom ones

class Sequence(ComfyWidgetType):
    TYPE = 'SEQUENCE'

class Job(ComfyWidgetType):
    TYPE = 'JOB'

class JobStep(ComfyWidgetType):
    TYPE = 'JOBSTEP'

# Workaround ComfyUI #257
Any = type('AnyType', (str, ), {'__ne__': lambda self, value: False})("*")


__all__ = ['Int', 'Float', 'String', 'Bool', 'Color', 'Combo', 'Any', 'Sequence', 'Job', 'JobStep']
