from totkn import *
import totkn
import pytest
import click
import yaml


import attr


def verify(expected, tekton_obj) -> None:
    if type(expected) == str:
        expected = yaml.load(expected, Loader=yaml.SafeLoader)
    result_str = tekton_obj.to_yaml()
    click.echo(result_str)
    result = yaml.load(result_str, Loader=yaml.SafeLoader)
    assert result == expected


ubuntu_task_str = """
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: mytask
spec:
  steps:
  - image: ubuntu
"""


def test_task_readme_example1() -> None:
    verify(ubuntu_task_str, Task(name="mytask", steps=[Step(image="ubuntu")]))


def xtest_task_readme_example2() -> None:
    click.echo(Task().to_yaml(check=False))


def test_task_str() -> None:
    step = totkn.Step("ubuntu")
    task = totkn.Task("mytask")
    task.steps = [step]
    verify(ubuntu_task_str, task)


def test_task_missing_step() -> None:
    task = totkn.Task("mytask")
    try:
        task.to_yaml()
    except MissingAttribute as ma:
        assert isinstance(ma, MissingAttribute)


def test_pipeline_str() -> None:
    task = totkn.Task("mytask")
    p = totkn.Pipeline(name="pipelinename")
    p.tasks = [PipelineTask("ptask", task.ref())]
    pt = totkn.PipelineTask()
    pt.name = "pipeline-taskref-name"
    verify(
        """
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: pipelinename
spec:
  tasks:
  - name: ptask
    taskRef:
      name: mytask
""",
        p,
    )


def test_trigger() -> None:
    task = totkn.Task("mytask")
    p = totkn.Pipeline(name="pipeline")
    p.tasks = [PipelineTask("ptask", task.ref())]
    pt = totkn.PipelineTask()
    pt.name = "pipeline-taskref-name"
    pr = PipelineRun("pipelinerun-$(uid)")
    pr.pipelineRef = p.ref()
    verify(
        """
      apiVersion: tekton.dev/v1beta1
      kind: PipelineRun
      metadata:
        name: pipelinerun-$(uid)
      spec:
        pipelineRef:
            name: pipeline
""",
        pr,
    )

    tt = TriggerTemplate("theTemplateTrigger")
    tt.resourcetemplates = [pr]
    verify(
        """
apiVersion: tekton.dev/v1alpha1
kind: TriggerTemplate
metadata:
  name: theTemplateTrigger
spec:
  resourcetemplates:
    - apiVersion: tekton.dev/v1beta1
      kind: PipelineRun
      metadata:
        name: pipelinerun-$(uid)
      spec:
        pipelineRef:
            name: pipeline
""",
        tt,
    )


def task_dict(name):
    return {
        "apiVersion": "tekton.dev/v1beta1",
        "kind": "Task",
        "metadata": {"name": name,},
    }


def xtest_task_dict():
    task = totkn.Task("secret-env-task")
    verify(task_dict("secret-env-task"), task)


from typing import List


def astr(a: str):
    pass


def xtest_task_description():
    t1 = totkn.Task("secret-env-task", description="the description")
    t1.params = [totkn.Param()]
    click.echo(t1.params)
    t1.steps = [totkn.Step(image="ubuntu")]
    d = task_dict("secret-env-task")
    d["metadata"]["annotations"] = {"description": "the description"}
    verify(d, t1)
    t2 = totkn.Task("secret-env-task")
    t2.description("the description")
    t2.steps.append(totkn.Step(image="ubuntu"))
    verify(d, t2)


def ztest_2():
    task = totkn.Task("secret-env-task")
    task_dict().update(
        {
            "spec": {
                "steps": [
                    {
                        "name": "echo",
                        "image": "ubuntu",
                        "command": "echo",
                        "args": "hello",
                    },
                ]
            }
        }
    )
