# totkn
Generate the tekton objects in python.  The name means from python **to tekton**

One to one mapping from python classes to tekton objects.  The python classes do not have the nesting required by tekton so:

```
python
>>> from totkn import *
>>> Task(name="mytask, steps=[ Step(image="ubuntu) ]).to_yaml()
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: mytask
spec:
  steps:
  - image: ubuntu
```

The above is type checked at runtime.  Get type checking, auto complete, etc in your IDE or using mypy to statically check your tekton objects while you type:

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
- Object model identical to tekton (nothing new to learn)
- Avoid repetition for things like parameter specficiations
- Create two pipelines with minor differences using python variables, if statements, functions, for, etc

# Type
|Tekton|Python|Notes|
|--|--|--|
|Task|Task|
|na|Step|Member of a Task steps list|
