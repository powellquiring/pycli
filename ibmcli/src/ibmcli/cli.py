#!/usr/bin/env python3

import subprocess, re, click
import ibmcli
import functools
import json

def log_command(command, **kwargs):
    print(' '.join(command) + '    ' + kwargs.get('delimiter', ''))
    if kwargs.get('dry_run', False):
        return
    stdout = ''
    try:
        out = subprocess.check_output(command)
        stdout = out.decode()
    except subprocess.CalledProcessError:
        print('*** Command execution failed')
    if kwargs.get('print_output', True):
        print(stdout)
    return stdout

def log_help_command(command, **kwargs):
    return log_command([*command, '--help'], **kwargs)

def get_commands(command, **kwargs):
    stdout = log_help_command(command, **kwargs)
    return ibmcli.get_commands_from_string(command, stdout)

def bad(left, right_lists):
    for right in right_lists:
        if left == right:
            return True # bad
    return False # good
def bad_child(parent, child):
    return bad([*parent, child], [['cfee', 'Example'],['cs', 'cluster', 'create']])
def bad_parent(parent):
    return bad(parent, [['ae', 'file-system'], ['ae', 'kernels'], ['at']])

def log_help_children(depth, parent, children):
    print('log_help_children', parent, children)
    if bad_parent(parent):
        print(f'\n\n*** Help command output for "{parent}" is bad and all his children are ignored\n\n')
        return
    for child in children:
        if bad_child(parent, child):
            print(f'\n\n*** Help command output for "{parent}" specifically the child "{child}" is bad and "{child}" is ignored\n\n')
            continue
        grand_children = get_commands(['ibmcloud', *parent, child], delimiter='####################################################################################################')
        log_help_children(depth+1, [*parent, child], grand_children)

def log_help_commands(top):
    if top:
        top_commands = [ *top ]
    else:
        top_commands = get_commands(['ibmcloud'], delimiter='====================================================================================================')
    log_help_children(0, [], top_commands)

def install_plugins(dry_run):
    stdout = log_command(['ibmcloud', 'plugin', 'repo-plugins'])
    for plugin in ibmcli.plugin_repo_plugins(stdout):
        command = ['ibmcloud', 'plugin', 'install', plugin.name, '-f']
        log_command(command, dry_run=dry_run)

def uninstall_plugins(dry_run):
    stdout = log_command(['ibmcloud', 'plugin', 'list'])
    for plugin in ibmcli.plugin_list(stdout):
        command = ['ibmcloud', 'plugin', 'uninstall', plugin.name]
        log_command(command, dry_run=dry_run)

def edit_doit(list_command, action_command, **kwargs):
    stdout = log_command(list_command)
    result = click.edit(stdout)
    if result:
        for id in ibmcli.id_list_from_editor_output(result, **kwargs):
            log_command(list((*action_command, id)))

def json_csv_edit_doit(json_command, fieldnames, fieldname, action_command_left, action_command_right, **kwargs):
    json_string = log_command(json_command, print_output=False, **kwargs)
    if kwargs.get('makearray', False):
        json_string='[' + ','.join(json_string.split('\n')[:-1]) + ']'
    csv_file_str = ibmcli.csv_file_str_from_json(json_string, fieldnames)
    if csv_file_str == None:
        click.echo('No objects')
        return
    csv_file_str = click.edit(csv_file_str)
    ids = ibmcli.ids_from_csv_file_str(csv_file_str, fieldnames, fieldname)
    for id in ids:
        log_command(list((*action_command_left, id, *action_command_right)))

def each_region():
    log_command([])


def sl_vs_cancel():
    edit_doit(['ibmcloud', 'sl', 'vs', 'list'], ['ibmcloud', 'sl', 'vs', 'cancel', '-f'])

def sl_image_delete():
    edit_doit(['ibmcloud', 'sl', 'image', 'list', '--private'], ['ibmcloud', 'sl', 'image', 'delete'])

def is_images_delete():
    edit_doit(['ibmcloud', 'is', 'images', '--visibility', 'private'], ['ibmcloud', 'is', 'image-delete', '-f'], header_lines=2)
    # TODO convert to json

def is_instances():
    log_command(['ibmcloud', 'is', 'instances'])

def is_instances_delete():
    json_csv_edit_doit(
        ['ibmcloud', 'is', 'instances', '--json'],
        ['name', 'created_at', 'name', 'memory', 'id'],
        'id',
        ['ibmcloud', 'is', 'instance-delete', '-f'], [])

def resource_service_instances_delete():
    log_command(['ibmcloud', 'target', '--unset-resource-group'])
    json_csv_edit_doit(
        ['ibmcloud', 'resource', 'service-instances', '--output', 'json'],
        ['name', 'region', 'type', 'subtype', 'id'],
        'id',
        ['ibmcloud', 'resource', 'service-instance-delete', '-f'], [])

def iam_access_groups_delete():
    json_csv_edit_doit(
        ['ibmcloud', 'iam', 'access-groups', '--output', 'json'],
        ['name', 'id', 'description'],
        'name',
        ['ibmcloud', 'iam', 'access-group-delete', '-f', '-r'], [])

def docker_ps_a_delete():
    json_csv_edit_doit(
        ['docker', 'ps', '-a', '--format', '{{json .}}'],
        ['Image', 'CreatedAt', 'Status', 'ID'],
        'ID',
        ['docker', 'rm'], [], makearray=True)

def docker_images_delete():
    json_csv_edit_doit(
        ['docker', 'images', '--format', '{{json .}}'],
        ['Repository', 'Image', 'CreatedAt', 'Status', 'ID'],
        'ID',
        ['docker', 'image', 'rm'], [], makearray=True)

def docker_images_delete_f():
    json_csv_edit_doit(
        ['docker', 'images', '--format', '{{json .}}'],
        ['Repository', 'Image', 'CreatedAt', 'Status', 'ID'],
        'ID',
        ['docker', 'image', 'rm'], ['-f'], makearray=True)


def kp_instances_delete():
    pass

def kp_keys_delete(guid):
    json_csv_edit_doit(
        ['ibmcloud', 'kp', '-i', guid, 'list', '--output', 'json'],
        ['name', 'creationDate', 'type', 'id'],
        'id',
        ['ibmcloud', 'kp', '-i', guid, 'delete'], [])

@click.group()
@click.option('-a', '--all', is_flag=True, help='repeat for all regions if the command supports regions')
@click.pass_context
def cli(ctx, all):
    ctx.ensure_object(dict)
    if all:
        ctx.obj['ALL_REGIONS'] = True
    else:
        ctx.obj['ALL_REGIONS'] = False

VPC_GENERATION_2 = None
def vpc_generation_2():
    global VPC_GENERATION_2
    if VPC_GENERATION_2 == None:
        stdout = log_command(['ibmcloud', 'is', 'target'])
        VPC_GENERATION_2 = (stdout.find('1') == -1)
    return VPC_GENERATION_2

def region_list_vpc():
    if vpc_generation_2():
        return ['us-south']

    stdout = log_command(['ibmcloud', 'regions', '--output', 'json'], print_output=False)
    list = json.loads(stdout)
    regions = [r['Name'] for r in list]
    [regions.remove(region) for region in ['in-che', 'jp-osa', 'us-south-test', 'kr-seo', 'us-east']]
    return regions

def all_regions(f):
    @functools.wraps(f)
    def all_regions_if_ctx(ctx, *args, **kwargs):
        if ctx.obj['ALL_REGIONS']:
            for r in region_list_vpc():
                log_command(['ibmcloud', 'target', '-r', r], print_output=False)
                f(ctx, *args, **kwargs)
        else:
                f(ctx, *args, **kwargs)
    return all_regions_if_ctx

@cli.group()
def plugin():
    pass

@plugin.command(help='uninstall all plugins')
@click.option('-d', '--dry-run', is_flag=True, help='print what it would do but do not do anything')
def uninstall(dry_run):
    uninstall_plugins(dry_run)

@plugin.command(help='install all plugins')
@click.option('-d', '--dry-run', is_flag=True, help='print what it would do but do not do anything')
def install(dry_run):
    install_plugins(dry_run)

@cli.command(help='generate help for all (or list of commands) and children')
@click.argument('top', nargs=-1)
def help(top):
    log_help_commands(top)

@cli.group()
def sl():
    pass

@sl.group()
def vs():
    pass

@vs.command(help='put a list of instances in a file for editing then delete the ones in the file')
def cancel():
    sl_vs_cancel()

@sl.group()
def image():
    pass

@image.command(help='put a list of --private images in a file for editing then delete the ones in the file')
def delete():
    sl_image_delete()

@cli.group('is')
def xis():
    pass

@xis.command(help='delete some images')
def images_delete():
    is_images_delete()

@xis.command(help='delete some images')
@click.pass_context
@all_regions
def instances_delete(ctx):
    is_instances_delete()

@xis.command(help='list instances')
@click.pass_context
@all_regions
def instances(ctx):
    is_instances()

@cli.group()
def resource():
    pass

@resource.command(help='delete some resource instances')
def service_instances_delete():
    resource_service_instances_delete()

@resource.command(help='delete some resource groups')
def service_instances_delete():
    resource_service_instances_delete()

@cli.group()
def iam():
    pass
@iam.command(help='edit a list of iam access groups and choose which ones to delete, this includes the keys in the instances')
def access_groups_delete():
    iam_access_groups_delete()

@cli.group()
def docker():
    pass
@docker.command(help='edit output of: docker ps -a, choose which ones to delete')
def ps_a_delete():
    docker_ps_a_delete()
@docker.command(help='edit output of: docker images, choose which ones to delete')
def images_delete():
    docker_images_delete()
@docker.command(help='edit output of: docker images, choose which ones to delete using force option')
def images_delete_f():
    docker_images_delete_f()

@cli.group()
def kp():
    pass

@kp.command(help='edit a list of key protect instances and choose which ones to delete, this includes the keys in the instances')
def instances_delete():
    kp_instances_delete()

@kp.command(help='edit a list of keys to delete from the instance identified by guid')
@click.argument('guid', nargs=1)
def keys_delete(guid):
    kp_keys_delete(guid)

#@cli.command(help='ibmcloud front end, might be useful for -a command')
#@click.pass_context
#@all_regions
#def ic(ctx):

#@cli.command(help='test stuff not useful')
#@click.pass_context
#@all_regions
def test(ctx):
    print('test')
#if __name__ == '__main__':
#    print('main')
#    print(dir())
#    cli()
