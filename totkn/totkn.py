import yaml
from typing import List, Union, List, Any, Dict, Tuple
import typing
import enum
import attr
import attrs_strict
from attrs_strict import type_validator


class MissingAttribute(Exception):
    pass


def yaml_dump(d):
    return yaml.dump(d, Dumper=yaml.Dumper)


def self_attributes(self, attrs):
    return {attr.name: getattr(self, attr.name) for attr in attrs}


@attr.s
class FileObject:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    description: Union[str, None] = attr.ib(default=None, validator=type_validator())
    apiVersion: str = attr.ib(default="tekton.dev/v1beta1", validator=type_validator())

    def asdict(self):
        def get_delete(d, key):
            v = d[key]
            del d[key]
            return v

        def transform_fileobject(d):
            if isinstance(d, dict):
                if "apiVersion" in d:
                    # If there is an apiVersion it is a file object.  Rearrange attributes
                    # Move all keys to the spec
                    spec = {}
                    for (key, val) in d.items():
                        spec[key] = val
                    for (key, val) in spec.items():
                        del d[key]
                    # create the file level attributes
                    d["metadata"] = {"name": get_delete(spec, "name")}
                    if "description" in spec:
                        d["metadata"]["description"] = get_delete(spec, "description")
                    d["kind"] = get_delete(spec, "kind")
                    d["apiVersion"] = get_delete(spec, "apiVersion")
                    d["spec"] = spec
                for (key, val) in d.items():
                    transform_fileobject(val)
            if isinstance(d, list):
                for i in d:
                    transform_fileobject(i)

        root = attr.asdict(self, filter=lambda attr, value: value != None)
        transform_fileobject(root)
        return root

    def to_yaml(self, **kwargs):
        if kwargs.get("check", True):
            self.semantic_check()
        return yaml_dump(self.asdict())


@attr.s
class FileObjectAlpha(FileObject):
    apiVersion: str = attr.ib(default="tekton.dev/v1alpha1", validator=type_validator())


@attr.s
class Step:
    image: str = attr.ib(default=None, validator=type_validator())
    args: Union[str, None] = attr.ib(default=None, validator=type_validator())
    command: Union[str, None] = attr.ib(default=None, validator=type_validator())
    env: Union[str, None] = attr.ib(default=None, validator=type_validator())


class ParamEnum(enum.Enum):
    str = enum.auto()
    list = enum.auto()


@attr.s
class Param:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    description: Union[str, None] = attr.ib(default=None, validator=type_validator())
    default: Union[str, None] = attr.ib(default=None, validator=type_validator())
    type: Union[ParamEnum, None] = attr.ib(default=None, validator=type_validator())


class Inputs:
    pass


class Resources:
    pass


@attr.s
class TaskSpec:
    steps: Union[None, List[Step]] = attr.ib(default=None, validator=type_validator())
    params: Union[None, List[Param]] = attr.ib(default=None, validator=type_validator())
    resources: Union[None, List[Resources]] = attr.ib(
        default=None, validator=type_validator()
    )


class TaskRun(FileObject):
    pass


@attr.s
class TaskRef:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())


@attr.s
class Task(FileObject, TaskSpec):
    kind: str = attr.ib(default="Task", validator=type_validator())

    def ref(self) -> TaskRef:
        tr = TaskRef()
        tr.name = self.name
        return tr

    def semantic_check(self):
        if self.steps == None or len(self.steps) == 0:
            raise MissingAttribute("Task object must have at least one step")


@attr.s
class PipelineTask:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    taskRef: Union[None, TaskRef] = attr.ib(default=None, validator=type_validator())
    params: Union[None, List[Param]] = attr.ib(default=None, validator=type_validator())


@attr.s
class PipelineSpec:
    tasks: Union[None, List[PipelineTask]] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class PipelineRef:
    name: str = attr.ib(default=None, validator=type_validator())


@attr.s
class Pipeline(FileObject, PipelineSpec):
    kind: str = attr.ib(default="Pipeline", validator=type_validator())

    def semantic_check(self):
        pass

    def ref(self) -> PipelineRef:
        return PipelineRef(self.name)


@attr.s
class PipelineRunSpec:
    params: Union[None, List[Param]] = attr.ib(default=None, validator=type_validator())
    pipelineRef: Union[None, PipelineRef] = attr.ib(
        default=None, validator=type_validator()
    )
    pipelineSpec: Union[None, PipelineSpec] = attr.ib(
        default=None, validator=type_validator()
    )
    serviceAccountName: Union[None, str] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class PipelineRun(FileObject, PipelineRunSpec):
    kind: str = attr.ib(default="PipelineRun", validator=type_validator())

    def semantic_check(self):
        pass


# TriggerResourceTemplates = Union[PipelineRun, ...]
TriggerResourceTemplates = PipelineRun


@attr.s
class TriggerTemplateSpec:
    resourcetemplates: Union[None, List[TriggerResourceTemplates]] = attr.ib(
        default=None, validator=type_validator()
    )
    params: Union[None, List[Param]] = attr.ib(default=None, validator=type_validator())


@attr.s
class TriggerTemplate(FileObjectAlpha, TriggerTemplateSpec):
    kind: str = attr.ib(default="TriggerTemplate", validator=type_validator())

    #    spec: Union[None, TriggerTemplateSpec] = attr.ib(
    #        default=None, validator=type_validator()
    #    )

    def semantic_check(self):
        pass
