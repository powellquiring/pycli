import yaml
from typing import List, Union, List, Any, Dict, Tuple
import typing
import collections
import enum
import abc


def yaml_dump(d):
    return yaml.dump(d, Dumper=yaml.Dumper)


def is_list(typ) -> bool:
    return typ._name == "List"


class Base(abc.ABC):
    def __init__(self):
        for (prop, type_required) in self.props:
            typ = type_required[0]
            # required = type_required[1]
            if is_list(typ):
                self.__setattr__(typ, list())

    @property
    @abc.abstractmethod
    def props(self) -> Dict[str, Tuple[Any, bool]]:
        return {}

    def to_dict(self):
        ret = {}
        for key, (_, required) in list(self.props.items()):
            if hasattr(self, key):
                val = self.__getattribute__(key)
                if isinstance(val, enum.Enum):
                    ret[key] = val.name
                else:
                    ret[key] = val
            else:
                if required:
                    type_name = self.__class__.__name__
                    raise ValueError(f"Resource {key} required in type {type_name}")
        return ret

    def to_yaml(self):
        return yaml_dump(self.to_dict())


class FileObject(Base):
    apiVersion = "tekton.dev/v1alpha1"

    specs: Dict[str, Union[Any, bool]] = {}  # override in derived class
    _props = {
        "name": (str, True),
        "description": (str, False),
    }

    # [[[cog
    # import coghelp
    # import totkn
    # coghelp.class_props(totkn.FileObject)
    # ]]]

    # [[[end]]]

    def to_base_types(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if isinstance(o, list):
            return [self.to_base_types(i) for i in o]
        return o

    def to_dict(self):
        """The base class dictionary is in a flat format with all attriabutes in the object"""
        selfd = super().to_dict()
        # now generate the tekton format
        ret = {
            "metadata": {"name": self.name},
            "kind": self.kind,
            "apiVersion": self.apiVersion,
        }
        for key, (typ, required) in list(self.specs.items()):
            l = self.__getattribute__(key)
            if len(l) > 0:
                if not "spec" in ret:
                    ret["spec"] = {}
                base = self.to_base_types(l)
                ret["spec"][key] = base
            else:
                if required:
                    type_name = self.__class__.__name__
                    r = f"Resource {key} required in type {type_name}"
                    if hasattr(self, "name"):
                        r = r + f" name {self.name}"
                    raise ValueError(r)

        return ret

    def to_yaml(self):
        return yaml_dump(self.to_dict())


class Step(Base):
    _props = {
        "image": (str, True),
        "args": (str, False),
        "command": (str, False),
        "env": (str, False),
    }
    # [[[cog
    # import coghelp
    # import totkn
    # ]]]
    # [[[end]]]

    def to_base_types(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if isinstance(o, list):
            return [self.to_base_types(i) for i in o]
        return o

    def to_dict(self):
        """The base class dictionary is in a flat format with all attriabutes in the object"""
        selfd = super().to_dict()
        # now generate the tekton format
        ret = {
            "metadata": {"name": self.name},
            "kind": self.kind,
            "apiVersion": self.apiVersion,
        }
        for key, (typ, required) in list(self.specs.items()):
            l = self.__getattribute__(key)
            if len(l) > 0:
                if not "spec" in ret:
                    ret["spec"] = {}
                base = self.to_base_types(l)
                ret["spec"][key] = base
            else:
                if required:
                    type_name = self.__class__.__name__
                    r = f"Resource {key} required in type {type_name}"
                    if hasattr(self, "name"):
                        r = r + f" name {self.name}"
                    raise ValueError(r)

        return ret

    def to_yaml(self):
        return yaml_dump(self.to_dict())


class ParamEnum(enum.Enum):
    str = enum.auto()
    list = enum.auto()


class Param(Base):
    _props = {
        "name": (str, True),
        "description": (str, False),
        "default": (str, False),
        "type": (ParamEnum, False),
    }

    # [[[cog
    # import coghelp
    # import totkn
    # coghelp.class_props(totkn.Param)
    # ]]]

    # [[[end]]]


class TaskRef:
    _props = {}


class Inputs:
    _props = {}


class Resources:
    _props = {}


class TaskSpec(Base):
    _props = {
        "steps": (List[Step], True),
        "params": (List[Param], False),
        "resources": (List[Resources], False),
    }
    # [[[cog
    # import coghelp
    # import totkn
    # coghelp.class_props(totkn.TaskSpec)
    # ]]]

    # [[[end]]]


class TaskRun(FileObject):
    _props = {}


class Task(FileObject, TaskSpec):
    """Task has the TaskSpec properties at the level of the Task.  It might be more logical
    to put it as a a child of the Task under the property 'spec' but that makes it more verbose"""

    kind = "Task"

    def to_dict(self):
        file_dict = FileObject.to_dict(self)
        file_dict["spec"] = TaskSpec.to_dict(self)


class Pipeline(FileObject):
    _props = {"tasks": (Union[TaskSpec, TaskRef], False)}
    # [[[cog
    # import coghelp
    # import totkn
    # coghelp.class_props(totkn.Pipeline)
    # ]]]

    # [[[end]]]

    def to_base_types(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()
        if isinstance(o, list):
            return [self.to_base_types(i) for i in o]
        return o

    def to_dict(self):
        """The base class dictionary is in a flat format with all attriabutes in the object"""
        selfd = super().to_dict()
        # now generate the tekton format
        ret = {
            "metadata": {"name": self.name},
            "kind": self.kind,
            "apiVersion": self.apiVersion,
        }
        for key, (typ, required) in list(self.specs.items()):
            l = self.__getattribute__(key)
            if len(l) > 0:
                if not "spec" in ret:
                    ret["spec"] = {}
                base = self.to_base_types(l)
                ret["spec"][key] = base
            else:
                if required:
                    type_name = self.__class__.__name__
                    r = f"Resource {key} required in type {type_name}"
                    if hasattr(self, "name"):
                        r = r + f" name {self.name}"
                    raise ValueError(r)

        return ret

    def to_yaml(self):
        return yaml_dump(self.to_dict())
