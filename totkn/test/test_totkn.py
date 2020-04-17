from totkn import *
import totkn
import pytest
import click
import yaml


import attr


def test_syntax() -> None:
    p = Pipeline(name="pl")
    s = p.to_yaml()
    click.echo(s)


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


def test_task_steps() -> None:
    step = totkn.Step()
    step.image = "ubuntu"
    step.name = "echo"
    step.command = ["echo"]
    step.args = ["01 version"]
    task = totkn.Task("the-task")
    task.steps = [step]
    verify(
        """
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: the-task
spec:
  steps:
    - name: echo
      image: ubuntu
      command:
        - echo
      args:
        - "01 version"

""",
        task,
    )


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


def test_trigger_exception() -> None:
    tt = TriggerTemplate()
    pr = PipelineRun("pipelinerun-$(uid)")
    tt.resourcetemplates = [pr]
    try:
        tt.to_yaml()
    except Exception as e:
        assert isinstance(e, MissingAttribute)
        return
    assert False


def test_trigger_binding() -> None:
    tb = TriggerBinding("theTriggerBinding")
    verify(
        """
apiVersion: tekton.dev/v1alpha1
kind: TriggerBinding
metadata:
  name: theTriggerBinding
""",
        tb,
    )


def test_event_listener() -> None:
    el = EventListener("the-listener")
    elt = EventListenerTrigger(
        binding=Ref("theTriggerBinding"), template=Ref("theTemplateTrigger")
    )
    el.triggers = [elt]
    verify(
        """
apiVersion: tekton.dev/v1alpha1
kind: EventListener
metadata:
  name: the-listener
spec:
  triggers:
    - binding:
        name: theTriggerBinding
      template:
        name: theTemplateTrigger
""",
        el,
    )


def task_dict(name):
    return {
        "apiVersion": "tekton.dev/v1beta1",
        "kind": "Task",
        "metadata": {"name": name,},
    }


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


import examples.lab1_simple.gen as lab1
import examples.lab2_parameters.gen as lab2


def lab_test(gen, fs) -> None:
    expected = []
    with open(fs + "/expected.yaml") as f:
        for doc in yaml.load_all(f, Loader=yaml.SafeLoader):
            expected.append(doc)
    s = gen()
    actual = []
    for doc in yaml.load_all(s, Loader=yaml.SafeLoader):
        actual.append(doc)
    for i in range(0, len(actual)):
        assert expected[i] == actual[i]
    assert len(expected) == len(actual)


def test_example_lab1() -> None:
    lab_test(lab1.gen, "examples/lab1_simple")


def test_example_lab2() -> None:
    lab_test(lab2.gen, "examples/lab2_parameters")
