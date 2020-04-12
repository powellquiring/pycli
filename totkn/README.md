# totkn

Generate the tekton objects in python. The name means from python **to tekton**

One to one mapping from python classes to tekton objects. The python classes do not have the nesting required by tekton so:

```
python
>>> from totkn import *
>>> Task(name="mytask", steps=[Step(image="ubuntu")]).to_yaml()
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: mytask
spec:
  steps:
  - image: ubuntu
```

The above is type checked at runtime and statically using type annotations to enable IDE auto complete and mypy.

```
$ cat mytask.py:
from totkn import *
step = Step()
step.image = "ubuntu" # must be a str
task = Task()
task.name = "mytask" # must be a str
task.steps = [ step ] # must be a sequence of Step
print(task.to_yaml())
$ mypy mytask.py
Success: no issues found in 1 source files
```

Nice stuff:

- Type checking and error checking of syntax before using tktn cli
- Avoid repetition for things like parameter specficiations
- Create two pipelines with minor differences using python variables, if statements, functions, for, etc

# Philosphy

The goal is to represent the tekton type system both tersly and accurately. High level objects are represented by a yaml file and structured consistently. This is straightforward

```
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: the-task-name
  description: details
```

Where do each of these come from?

- apiVersion: tekton.dev/v1alpha1 - Task class
- kind: Task - Task class
- metadata: Task class
- name: the-task-name - instance of Task class
- description: details - instance of Task class

```
$ python
from totkn import *
>>> Task().to_yaml(check=False)
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: None
spec:
  steps: {}
```

The name and description then come from the task instance. To keep the definition terse a Task composition of the `spec` is not used and instead inheritance adds steps, params, ... directly to the Task. So instead of:

```
Task().spec = TaskSpec(steps=[Step()])
```

The following terse representation is used:

```
Task().steps = [Step()]
```

Other tekton types can not be simplified without defining a unique class hierarchy. A PipeLineRun is composed of a PipelineRunSpec, PipelineRef or PipelineSpec, ... Wow. Totkn must thinly layer on Tekton. It should be possible to read the Tekton documentation an use totkn without much effort. The underlying structure of Tekton is going to shine through to totkn in these cases.

```
prs = PiplineRunSpec()
prs.pipelineRef = PipelineRef("mypipeline")
PipelineRun().spec = prs
```

or

```
PipelineRun(name="mypiplinerun", spec=PipelineRunSpec(pipelineRef=PipelineRef(name="mypipeline")))
```

A simplification of the Tekton model is provided by additional classes that start with `I`. Special cases implemented with Inheritance instead of composition. For eample the class IPipelineRunSpecRef is a PiplineRunSpec() which inherits PipelineRef to allow:

````
PipelineRun(name="mypiplinerun", spec=IPipelineRunSpecRef(name="mypipeline"))
```
There is also a `class IPipelineRunSpecSpec(PipelineSpec)` that is a PipelineRunSpec


The naming of the I classes is add hoc.

# FileObject
- name:str
- description: str
# Task
class Task(FileObject, TaskSpec)
- steps
- params
# Pipeline
class Pipeline(FileObject, PipelineSpec)
# PipelineRun
class PipelineRun(FileObject, PipelineRunSpec)
# PipelineRunSpec
class PipelineRunSpec()
class IPipelineRunSpecRef(PipelineRunSpec, PipelineRef)

# Type

| Tekton | Python | Notes                       |
| ------ | ------ | --------------------------- |
| Task, TaskSpec   | Task   |
| na     | Step   | Member of a Task steps list |

````

```

```
