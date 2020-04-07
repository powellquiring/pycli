import totkn
import pytest
import click
import yaml


def test_syntax() -> None:
    ts = totkn.TaskSpec()
    assert ts.steps == []


def task_secret_env_task():
    return """
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: secret-env-task
"""


def verify(expected, tekton_obj) -> None:
    if type(expected) == str:
        expected = yaml.load(expected, Loader=yaml.SafeLoader)
    result_str = tekton_obj.to_yaml()
    result = yaml.load(result_str, Loader=yaml.SafeLoader)
    assert result == expected


def xtest_task_str() -> None:
    step = totkn.Step()
    step.image = "ubuntu"  # must be a str
    task = totkn.Task()
    task.name = "mytask"  # must be a str
    task.steps.append(step)
    verify(
        """
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: mytask
spec:
  steps:
  - image: ubuntu
""",
        task,
    )


def xtest_pipeline_str() -> None:
    pt = totkn.PipelineTask()

    step = totkn.Step()
    step.image = "ubuntu"  # must be a str
    task = totkn.Task()
    task.name = "mytask"  # must be a str
    task.steps.append(step)
    verify(
        """
apiVersion: tekton.dev/v1alpha1
kind: Task
metadata:
  name: mytask
spec:
  steps:
  - image: ubuntu
""",
        task,
    )


def task_dict(name):
    return {
        "apiVersion": "tekton.dev/v1alpha1",
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
    t1.params.append(totkn.Param())
    click.echo("bef")
    click.echo(t1.params)
    click.echo("aft")
    t1.steps.append(totkn.Step(image="ubuntu"))
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
