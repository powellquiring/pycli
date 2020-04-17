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


class Base:
    def _semantic_check(self):
        pass


@attr.s
class Ref:
    name: str = attr.ib(default=None, validator=type_validator())


@attr.s
class FileObject(Base):
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    description: Union[str, None] = attr.ib(default=None, validator=type_validator())
    apiVersion: str = attr.ib(default="tekton.dev/v1beta1", validator=type_validator())

    def asdict(self):
        def get_delete(d, key):
            v = d[key]
            del d[key]
            return v

        def rewrite_if_fileobject(d):
            if "apiVersion" in d:
                # If there is an apiVersion it is a file object.  Rearrange attributes
                # Move all keys to the spec
                spec = {}
                for (key, val) in d.items():
                    spec[key] = val
                for (key, val) in spec.items():
                    del d[key]
                # create the file level attributes
                d.update(
                    {
                        "metadata": {"name": get_delete(spec, "name")},
                        "kind": get_delete(spec, "kind"),
                        "apiVersion": get_delete(spec, "apiVersion"),
                    }
                )
                if len(spec) > 0:
                    d["spec"] = spec
                if "description" in spec:
                    d["metadata"]["description"] = get_delete(spec, "description")

        def rewrite_fileobjects(d):
            if isinstance(d, dict):
                rewrite_if_fileobject(d)
                for (key, val) in d.items():
                    rewrite_fileobjects(val)
            if isinstance(d, list):
                for i in d:
                    rewrite_fileobjects(i)

        root = attr.asdict(self, filter=lambda attr, value: value != None)
        # asdict returned a dictionary that is specified correctly except the Fileobjects
        rewrite_fileobjects(root)
        return root

    def to_yaml(self, **kwargs):
        if kwargs.get("check", True):
            self._semantic_check()
        return yaml_dump(self.asdict())

    def _semantic_check(self):
        if self.name == None:
            raise MissingAttribute(f"{str(self.__class__)} must have a name")

    def ref(self) -> Ref:
        return Ref(self.name)


@attr.s
class FileObjectAlpha(FileObject):
    apiVersion: str = attr.ib(default="tekton.dev/v1alpha1", validator=type_validator())


@attr.s
class EnvVar:
    name: str = attr.ib(default=None, validator=type_validator())
    value: Union[str, None] = attr.ib(default=None, validator=type_validator())


@attr.s
class Step:
    image: Union[str, None] = attr.ib(default=None, validator=type_validator())
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    workingDir: Union[str, None] = attr.ib(default=None, validator=type_validator())
    args: Union[List[str], None] = attr.ib(default=None, validator=type_validator())
    command: Union[List[str], None] = attr.ib(default=None, validator=type_validator())
    # EnvFrom []EnvFromSource
    env: Union[List[EnvVar], None] = attr.ib(default=None, validator=type_validator())
    # VolumeMounts []VolumeMount


class ParamEnum(enum.Enum):
    str = enum.auto()
    list = enum.auto()


@attr.s
class Param:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    value: Union[str, None] = attr.ib(default=None, validator=type_validator())


@attr.s
class ParamSpec:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    description: Union[str, None] = attr.ib(default=None, validator=type_validator())
    default: Union[str, None] = attr.ib(default=None, validator=type_validator())
    type: Union[ParamEnum, None] = attr.ib(default=None, validator=type_validator())

    def ref(self) -> str:
        return f"$(params.{self.name})"


class Inputs:
    pass


class Resources:
    pass


@attr.s
class TaskSpec:
    steps: Union[None, List[Step]] = attr.ib(default=None, validator=type_validator())
    params: Union[None, List[ParamSpec]] = attr.ib(
        default=None, validator=type_validator()
    )
    resources: Union[None, List[Resources]] = attr.ib(
        default=None, validator=type_validator()
    )


class TaskRun(FileObject):
    pass


@attr.s
class Task(FileObject, TaskSpec):
    kind: str = attr.ib(default="Task", validator=type_validator())

    def _semantic_check(self):
        if self.steps == None or len(self.steps) == 0:
            raise MissingAttribute("Task object must have at least one step")


@attr.s
class PipelineTask:
    name: Union[str, None] = attr.ib(default=None, validator=type_validator())
    taskRef: Union[None, Ref] = attr.ib(default=None, validator=type_validator())
    params: Union[None, List[Param]] = attr.ib(default=None, validator=type_validator())


@attr.s
class PipelineSpec:
    tasks: Union[None, List[PipelineTask]] = attr.ib(
        default=None, validator=type_validator()
    )
    params: Union[None, List[ParamSpec]] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class Pipeline(FileObject, PipelineSpec):
    kind: str = attr.ib(default="Pipeline", validator=type_validator())


@attr.s
class PipelineRunSpec:
    params: Union[None, List[ParamSpec]] = attr.ib(
        default=None, validator=type_validator()
    )
    pipelineRef: Union[None, Ref] = attr.ib(default=None, validator=type_validator())
    pipelineSpec: Union[None, PipelineSpec] = attr.ib(
        default=None, validator=type_validator()
    )
    serviceAccountName: Union[None, str] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class PipelineRun(FileObject, PipelineRunSpec):
    kind: str = attr.ib(default="PipelineRun", validator=type_validator())


# TriggerResourceTemplates = Union[PipelineRun, ...]
TriggerResourceTemplates = PipelineRun


@attr.s
class TriggerTemplateSpec:
    resourcetemplates: Union[None, List[TriggerResourceTemplates]] = attr.ib(
        default=None, validator=type_validator()
    )
    params: Union[None, List[ParamSpec]] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class TriggerTemplate(FileObjectAlpha, TriggerTemplateSpec):
    kind: str = attr.ib(default="TriggerTemplate", validator=type_validator())


@attr.s
class TriggerBindingSpec:
    params: Union[None, List[ParamSpec]] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class TriggerBinding(FileObjectAlpha, TriggerBindingSpec):
    kind: str = attr.ib(default="TriggerBinding", validator=type_validator())


@attr.s
class EventListenerTrigger:
    binding: Union[None, Ref] = attr.ib(default=None, validator=type_validator())
    template: Union[None, Ref] = attr.ib(default=None, validator=type_validator())


@attr.s
class EventListenerSpec:
    triggers: Union[None, List[EventListenerTrigger]] = attr.ib(
        default=None, validator=type_validator()
    )


@attr.s
class EventListener(FileObjectAlpha, EventListenerSpec):
    kind: str = attr.ib(default="EventListener", validator=type_validator())
