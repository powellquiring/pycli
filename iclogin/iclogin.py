import click
import json
import subprocess
from pathlib import Path

def log_command(command, print_output=True, dry_run=False, delimiter=""):
    click.echo(" ".join(command) + "    " + delimiter)
    if dry_run:
        return
    stdout = ""
    try:
        out = subprocess.check_output(command)
        stdout = out.decode()
    except subprocess.CalledProcessError:
        click.echo("*** Command execution failed")
    if print_output:
        click.echo(stdout)
    return stdout


def default_dir():
    return Path.home() / "apikeys"


suffixes_long_to_short = (".apiKey.json", ".json", "")


def list_all(defaultdir, dump, output, dump_errors):
    (goods, errors) = parse_dir(defaultdir)
    if dump_errors:
        for (f, error) in errors:
            click.echo(error)
    for (name, key) in goods:
        if dump:
            click.echo(f"{key} : {name}")
        else:
            click.echo(f"icl {name}")


def parse_dir(defaultdir):
    click.echo(f"looking in {str(defaultdir)}")
    errors = []
    goods = []
    for default_dir_file in defaultdir.glob("*"):
        if default_dir_file.is_file():
            for endswith in suffixes_long_to_short:
                if default_dir_file.name.endswith(endswith):
                    name = default_dir_file.name.rstrip(endswith)
                    (f, apikey, err) = find_target(defaultdir, name)
                    if f == None:
                        errors.append(
                            (f, f"{name} will not work, this is the error {err}")
                        )
                    else:
                        (apikey, err) = file_to_key(f)
                        if apikey == None:
                            errors.append((f, err))
                        else:
                            goods.append((name, apikey))
                    break
    return (goods, errors)


def find_target(defaultdir, target) -> Path:
    "return (f, key, error) key in the first file found with the right suffix"
    f = Path(target)
    if f.exists():
        (key, err) = file_to_key(f)
        if key != None:
            return (target, key, None)
        else:
            return (None, None, err)
        return (f, None)
    if len(f.parts) > 1:  # full path name and it does not exist so quit
        return (None, None, f"full path name for a non existant file given: {f}")
    suffixes_sort_to_long = list(suffixes_long_to_short)
    suffixes_sort_to_long.reverse()
    matches = []
    all_files_attempted = []
    for suffix in suffixes_sort_to_long:
        file_name = f"{target}{suffix}"
        f = defaultdir / file_name
        all_files_attempted.append(f)
        if f.exists():
            (key, err) = file_to_key(f)
            if key != None:
                matches.append((f, key, None))
    if len(matches) == 0:
        return (None, None, f"tried these but no luck {all_files_attempted}")
    elif len(matches) > 1:
        return (None, None, f"all of these files matched correct {defaultdir}: {goods}")
    else:
        return matches[0]


def file_to_key(file):
    with file.open() as fp:
        try:
            contents = json.load(fp)
        except json.decoder.JSONDecodeError:
            return (
                None,
                f"not a json file",
            )
        keys = ["apikey", "apiKey"]
        for key in keys:
            if key in contents:
                return (contents[key], None)
        return (
            None,
            f"Json file does not include the expected json key, expecting one of: {str(keys)}",
        )


def get_resource_group():
      target = json.loads(log_command(["ibmcloud", "target", "--output", "json"], print_output=False))
      if "resource_group" in target:
        if "name" in target["resource_group"]:
          return target["resource_group"]["name"]
      return None

def set_resource_group(resource_group):
    log_command(["ibmcloud", "target", "-g", resource_group])

def login(file, dump, output):
    (f, apikey, err) = find_target(default_dir(), file)
    if f == None:
        click.echo(err)
        return
    if dump:
        if output == "json":
            click.echo(json.dumps({"apikey":f"{apikey}", "name": f"{f.name}"}))
        else:
            click.echo(f"{apikey} {f.name}")
    else:
        click.echo(f"using {str(f)}")
        resource_group = get_resource_group()
        log_command(["ibmcloud", "login", "--apikey", apikey])
        if resource_group:
          set_resource_group(resource_group)


@click.command()
@click.argument("target", nargs=1, required=False)
@click.option("-d", "--dump", is_flag=True, help="dump just the api keys, do not login")
@click.option("-o", "--output", type=click.Choice(['json', 'text'], case_sensitive=False), default="text")
@click.option("-e", "--dump_errors", is_flag=True, help="dump errors")
def cli(target, dump, dump_errors, output):
    """Simplify the login process by using apikeys, eventually it will: ibmcloud login --apikey x

    TARGET - name in the HOME/apikey direcgory appending .apiKey.json and .json, or provide a full path name
    if no TARGET provided then list all targets in ~/apikeys dir
    """
    if target == None:
        list_all(default_dir(), dump, output, dump_errors)
        return
    login(target, dump, output)


if __name__ == "__main__":
    cli()
