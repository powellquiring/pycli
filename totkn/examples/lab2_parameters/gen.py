import click
import copy
from totkn import *


def document_out(tkn) -> str:
    return "---\n" + tkn.to_yaml()


def gen():
    steps = [
        Step(
            name="echoenvvar",
            image="ubuntu",
            env=[EnvVar("VAR", "$(inputs.params.var)")],
            command=["/bin/bash"],
            args=["-c", "$(inputs.params.var)"],
        ),
        Step(
            name="echoenvvar",
            image="ubuntu",
            env=[EnvVar("VAR", "$(inputs.params.var)")],
            command=["/bin/bash"],
            args=["-c", "echo 01 lab2 env VAR: $VAR"],
        ),
        Step(
            name="echovar",
            image="ubuntu",
            command=["/bin/echo"],
            args=["$(inputs.params.var)"],
        ),
        Step(
            name="shellscript",
            image="ubuntu",
            env=[EnvVar("VAR", "$(inputs.params.var)")],
            command=["/bin/bash", "-c"],
            args=[
                """echo this looks just like a shell script and the '$ ( inputs.params.var ) ' is subbed in here: '$(inputs.params.var)'
env | grep VAR
echo done with shellscript
""",
            ],
        ),
    ]

    t1 = Task(name="the-var-task", steps=steps)
    var = ParamSpec(name="var", description="var example in task", default="VALUE")
    t1.params = [var]
    p1 = Pipeline(name="pipeline-no-variable")
    ptask1 = PipelineTask("pdv", taskRef=t1.ref())
    p1.tasks = [ptask1]
    pr1 = PipelineRun(name="pipelinerun-$(uid)")
    pr1.pipelineRef = p1.ref()
    tt1 = TriggerTemplate(name="trigger-pipeline-no-variable")
    tt1.resourcetemplates = [pr1]
    tb = TriggerBinding("simple-binding")
    el1 = EventListener("task-default-variable")
    el1.triggers = [EventListenerTrigger(binding=tb.ref(), template=tt1.ref())]

    p2 = Pipeline(name="pipeline-supplied-variable")
    ptask2 = copy.copy(ptask1)
    ptask2.params = [Param(name="var", value="PIPELINE_SUPPLIED")]
    ptask2.name = "pdv"
    p2.tasks = [ptask2]
    pr2 = copy.copy(pr1)
    pr2.pipelineRef = p2.ref()
    tt2 = TriggerTemplate(name="trigger-pipeline-supplied-variable")
    tt2.resourcetemplates = [pr2]
    el2 = EventListener("pipeline-supplied-variable")
    el2.triggers = [EventListenerTrigger(binding=tb.ref(), template=tt2.ref())]

    p3 = Pipeline(name="pipeline-input-parameter-variable")
    var_pipeline = ParamSpec(name="var", description="var example in pipeline")
    p3.params = [var_pipeline]
    ptask3 = copy.copy(ptask1)
    params = [Param(name="var", value=var_pipeline.ref())]
    ptask3.params = params
    ptask3.name = "pdv"
    p3.tasks = [ptask3]
    pr3 = copy.copy(pr1)
    pr3.pipelineRef = p3.ref()
    pr3.params = params
    tt3 = TriggerTemplate(name="trigger-user-supplied-variable")
    tt3.params = [ParamSpec(name="var", description="var example")]
    tt3.resourcetemplates = [pr3]
    el3 = EventListener("user-defined-variable")
    el3.triggers = [EventListenerTrigger(binding=tb.ref(), template=tt3.ref())]

    # dump out the file
    ret = document_out(el1)
    ret += document_out(tt1)
    ret += document_out(p1)
    ret += document_out(el2)
    ret += document_out(tt2)
    ret += document_out(p2)
    ret += document_out(el3)
    ret += document_out(tb)
    ret += document_out(tt3)
    ret += document_out(p3)
    ret += document_out(t1)
    return ret


if __name__ == "__main__":
    click.echo(gen())
