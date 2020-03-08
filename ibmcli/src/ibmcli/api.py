"""Main API for tasks project."""
import re
import json
import io
import csv
from collections import namedtuple
Plugin = namedtuple('Plugin', ['name', 'aliases', 'version', 'status', 'description'])

def split_line(s, start1, start2):
    return (s[0:start1].strip(), s[start1:start2].strip(), s[start2:].strip())

def deleteme():
    # past the COMMANDS and onto the next line:
    m = re.match(r".*(Plugin Name).*(Version).*(Status)\n", s, flags=re.DOTALL)
    if not m:
        return []
    name_start = m.start(1)
    version_start = m.start(2)-name_start
    status_start = m.start(3)-name_start

    # the command is the first word from each line following the COMMANDS: line, stop at the first blank line
    ret = []
    rest = s[m.end():]
    for line in rest.split('\n'):
        (names, version, status) = split_line(line, version_start, status_start)
        name_parts = names.split('/')
        name = name_parts[0]
        aliases = name_parts[1:]
        ret.append(Plugin(name=name, aliases=aliases, version=version, status=status, description=''))

def parts_matching_headers(s, *headers):
    match_string = ''.join([fr'.*({h})' for h in headers]) + " *\n"
    m = re.match(match_string, s, flags=re.DOTALL)
    column_starts = [m.start(i) - m.start(1) for i in range(1, len(headers) + 1)]
    column_starts.append(None)
    rest = s[m.end():]
    for line in rest.split('\n'):
        if line.strip() == '':
            break
        yield [line[column_starts[i]:column_starts[i + 1]].strip() for i in range(len(headers))]
    
def plugin_list_generator(s):
    """Plugins that have been installed"""
    # s is somethig like this:
    # Listing installed plug-ins...
    #
    #Plugin Name                                 Version   Status
    #dev                                         2.4.0
    #cloud-functions/wsk/functions/fn            1.0.35
    #container-service/kubernetes-service        0.4.38    Update Available
    #
    for line_parts in parts_matching_headers(s, 'Plugin Name', 'Version', 'Status'):
        name_parts = line_parts[0].split('/')
        yield Plugin(name=name_parts[0], aliases=name_parts[1:], version=line_parts[1], status=line_parts[2], description='')

def plugin_list(s):
    """return all of the plugins"""
    return [plugin for plugin in plugin_list_generator(s)]

def plugin_repo_plugins_generator(s):
    """Pull out Plugin types from the 'ibmcloud plugin repo-plugins' string provided"""
    #Getting plug-ins from all repositories...
    #
    #Repository: IBM Cloud
    #Status             Name                                        Versions                       Description
    #Update Available   container-service/kubernetes-service        0,0.1...                       yada zada
    for line_parts in parts_matching_headers(s, 'Status', 'Name', 'Versions', 'Description'):
        name_parts = line_parts[1].split('/')
        yield Plugin(status=line_parts[0], name=name_parts[0], aliases=name_parts[1:], version=line_parts[2], description=line_parts[3])

def plugin_repo_plugins(s):
    """return all of the plugins"""
    return [plugin for plugin in plugin_repo_plugins_generator(s)]

blank_line = re.compile(r"\s*\n")
sub_command = re.compile(r"\s*([\w-]+).*")
def words_until_blank_line(rest):
    ret = []
    while True:
        m = blank_line.match(rest)
        if m:
            return (ret, rest)
        m = sub_command.match(rest)
        if m:
            sub_command_str = m.group(1)
            ret.append(sub_command_str)
            rest = rest[m.end() + 1:]
        else:
            return (ret, rest)

COMMANDS_colon = re.compile(r".*COMMANDS:[^a-zA-Z]*", flags=re.DOTALL)
Commands_colon = re.compile(r".*?Commands:[^a-zA-Z]*", flags=re.DOTALL)
def get_commands_from_string(command, stdout):
    ret = []

    # past the COMMANDS and onto the next line:
    m = COMMANDS_colon.match(stdout)
    if not m:
        return []
    # the command is the first word from each line following the COMMANDS: line, stop at the first blank line
    rest = stdout[m.end():]
    if command == [ 'ibmcloud', 'cs']:
        print('YYYEEESS YES yes')
        while True:
            m = Commands_colon.match(rest)
            if m:
                rest = rest[m.end():]
                ret2, rest = words_until_blank_line(rest)
                ret.extend(ret2)
            else:
                break
    else:
        ret, rest = words_until_blank_line(rest)
    return ret


def id_list_from_editor_output(bs, **kwargs):
    """bs is a string of console output the lines are:
    # delete me if you .... (must be deleted)
    id     col1    col2
    010101 c11     c22222 ...
    
    If first line begins with # then return an empty list
    Ignore the second line
    Return a list composed of the first column in the rest of document
    Stop at end of file or first empty line
    """
    ret = []
    header_lines = kwargs.get("header_lines", 1)
    #lines = bs.decode("utf-8").split('\n')
    lines = bs.split('\n')
    if (lines[0][0:1] == '#'):
        return ret
    for line in lines[header_lines:]:
        cols = line.split()
        if len(cols) == 0:
            return ret
        ret.append(cols[0])
    return ret

def csv_file_str_from_json(json_s, fieldnames):
    """return a csv file contents string from a json string that must be an array of objects"""
    instances = json.loads(json_s)
    if len(instances) == 0:
        return None
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames, extrasaction='ignore', dialect='editor') 
    writer.writeheader()
    writer.writerows(instances)
    return out.getvalue()
    
def ids_from_csv_file_str(csv_file_str, fieldnames, fieldname):
    """return a set of ids from a string that is the contents of a file string
    fieldnames is all the field names in the file
    fieldname is one of the fieldnamds that is the id"""
    infile = io.StringIO(csv_file_str)
    reader = csv.DictReader(infile, fieldnames, dialect='editor')
    ret = []
    for row in reader:
        if set(row.values()) == set(fieldnames):
            continue # first row might be the title
        ret.append(row[fieldname])
    return ret

csv.register_dialect('editor', delimiter='\t')
