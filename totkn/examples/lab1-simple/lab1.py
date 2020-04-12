import click
from totkn import *
t = Task(name="the-task", steps=[Step(image="ubuntu")])
p = Pipeline(name="pipeline", tasks=[PipelineTask("xx1", taskRef=t.ref())])
click.echo(p.to_yaml())
click.echo("----------")
click.echo(t.to_yaml())

