#!/usr/bin/env python
import click
import subprocess
import json
import pendulum
import functools
import typer
import procin
from typing import Optional

runner = procin.Command(cache=True, cache_dir="rc", json=True)

@functools.lru_cache(maxsize=1)
def resource_groups():
    rgs = runner.run(['ibmcloud','resource','groups','--output','json'])
    rgid_rg = {}
    for rg in rgs:
        click.echo(f'{rg["name"]} {rg["id"]}')
        rgid_rg[rg["id"]] = rg
    return {**rgid_rg, **{"*": {"name": "*", "id": "*"}}}

@functools.lru_cache(maxsize=1)
def ic_resource_service_instances():
    return runner.run(['ibmcloud','resource','service-instances','--type','all','--all-resource-groups','--output','json'])

@functools.lru_cache(maxsize=1)
def ic_is_keys_by_id():
    stdout = runner.run(['ibmcloud','is','keys','--json'])
    return {k["id"]:k for k in json.loads(stdout)}

def ic_iam_access_group_policies(group):
    stdout = runner.run(['ibmcloud','iam','access-group-policies',group,'--output','json'])
    return json.loads(stdout)


@functools.lru_cache(maxsize=1)
def ic_iam_access_groups():
    stdout = runner.run(['ibmcloud','iam','access-groups','--output','json'])
    return json.loads(stdout)

def dump_resources(resource_list):
    rg_resource = {}
    for resource in resource_list:
        rg_resource.setdefault(resource["resource_group_id"], list()).append(resource)
    for (rg, resources) in rg_resource.items():
        click.echo(f'{resource_groups()[rg]["name"]}')
        rl = sorted(resources, key=lambda r: f'{r["resource_id"]}|{r["updated_at"]}')
        for resource in rl:
            click.echo(f'  {resource["resource_id"]} {resource["updated_at"]} {resource["name"]} {resource_groups()[resource["resource_group_id"]]["name"]} {resource["id"]}')

def dump_resources_crn(resource_list):
    for resource in resource_list:
        click.echo(resource["id"])

def default_name(resource, name):
    return resource_groups()[resource["resource_group_id"]]["name"] == "default" and resource["name"] == name

#now = pendulum.now()
def keep_resource(resource):
    return default_name(resource, "pfq") or default_name(resource, "cis-master") or default_name(resource, "bridgepy02-cos") or default_name(resource, "bridgepy02-fn") or resource["resource_id"] == "public.bluemix.container.registry"
    # a few ids like this one: 556153d0-5ad0-11e9-b7f9-41319ef22125
    # if len(resource["resource_id"]) > 33:
    #     return False
    # global now
    # date_string = resource["updated_at"][0:-1]
    # updated_at = pendulum.parse(date_string)
    # if updated_at.diff(now).in_days() > 90:
    #     return True
    # else:
    #     return False

# Used this to sort and display resources for deletion
def clean_resources():
    keep = []
    rm = []
    for resource in ic_resource_service_instances():
        if keep_resource(resource):
            keep.append(resource)
        else:
            rm.append(resource)
    click.echo("--- keepers ---")
    dump_resources(keep)
    click.echo("--- rm full ---")
    dump_resources(rm)
    click.echo("--- rm crn ---")
    dump_resources_crn(rm)

class Policy:
    is_attribute_names = set([
        "vpnGatewayId",
        "publicGatewayId",
        "flowLogCollectorId",
        "networkAclId",
        "vpcId",
        "subnetId",
        "securityGroupId",
        "instanceId",
        "volumeId",
        "floatingIpId",
        "keyId",
        "imageId",
        "instanceGroupId",
        "dedicatedHostId",
        "loadBalancerId",
    ])
    
    def __init__(self, policy):
        self.policy = policy
        access_groups = {e["id"]: e["name"] for e in ic_iam_access_groups()}
        self.parse_resources()
    def dump(self):
        click.echo(json.dumps(self.policy, indent=2))
    def access_group_name(self):
        assert len(self.policy["subjects"]) == 1
        assert len(self.policy["subjects"][0]["attributes"]) == 1
        assert self.policy["subjects"][0]["attributes"][0]["name"] == "access_group_id"
        return self.access_groups[self.policy["subjects"][0]["attributes"][0]["value"]]
    def role_str(self, role):
        #reduce to role-Editor or serviceRole-Manager crn:v1:bluemix:public:iam::::role:Editor crn:v1:bluemix:public:iam::::serviceRole:Manager
        ret = role.split(':')
        return f"{ret[-2]}-{ret[-1]}"
        
    def roles(self):
        #"roles": [
        #  {
        #    "role_id": "crn:v1:bluemix:public:iam::::role:Editor",
        #    "display_name": "Editor",
        #    "description": "As an editor, you can perform all platform actions except for managing the account and assigning access policies."
        #  }
        #],
        return ",".join([self.role_str(r["role_id"]) for r in self.policy["roles"]])
    def resource_group(self):
        return self.resource_group_str
    def resources(self):
        return self.resources_str

    def parse_resources(self):
        self.resource_group_str = ""
        self.resources_str = ""
        #"resources": [
        #  {
        #    "attributes": [
        #      {
        #        "name": "serviceName",
        #        "operator": "stringEquals",
        #        "value": "is"
        #      },
        #      {
        #        "name": "resourceGroupId",
        #        "operator": "stringEquals",
        #        "value": "740522abf40a44818a2b46f2f7f52dcc"
        #      },
        #      {
        #        "name": "vpcId",
        #        "operator": "stringEquals",
        #        "value": "*"
        #      },
        #      {
        #        "name": "accountId",
        #        "operator": "stringEquals",
        #        "value": "713c783d9a507a53135fe6793c37cc74"
        #      }
        #    ]
        #  }
        def attribute_string(attributes):
            ret = []
            #name2attribute = {}
            for attribute in attributes:
                assert attribute["operator"] == "stringEquals"

                for k,v in attribute.items():
                    if k == "name":
                        if v == "serviceName":
                            ret.append(f'sn:{attribute["value"]}')
                        elif v == "resourceGroupId":
                            self.resource_group_str = resource_groups()[attribute["value"]]["name"]
                        elif v == "accountId":
                            pass
                        elif v in self.is_attribute_names:
                            # assert attribute["value"] == "*"
                            if attribute["value"] == "*":
                                ret.append(f'{v}=*')
                            else:
                                if v == "keyId":
                                    ret.append(f'{v}={ic_is_keys_by_id()[attribute["value"]]["name"]}')
                                else:
                                    ret.append(f'{v}={attribute["value"]}')
                        elif v == "resourceType":
                            ret.append(f'rt:{attribute["value"]}')
                        elif v == "resource":
                            # TODO hope it is a resource group ID
                            if attribute["value"] in resource_groups():
                                ret.append(f'rg:{resource_groups()[attribute["value"]]["name"]}')
                            else:
                                ret.append(f"unknown resource attribute with name resource {json.dumps(attribute)}")
                                # raise Exception(f"unknown resource attribute with name resource {json.dumps(attribute, indent=2)}")
                        elif v == "serviceType":
                            ret.append(f'st-{attribute["value"]}')
                        else:
                            raise Exception(f"unknown resource attribute: ({k},{v}) {json.dumps(attribute)}")
            self.resources_str =  ",".join(ret)

        ret = ''
        for r in self.policy["resources"]:
            for key, value in r.items():
                assert key == "attributes"
                assert ret == ''
                ret = attribute_string(value)
        return ret
                
def table(group, dump):
    agp = ic_iam_access_group_policies(group)
    click.echo(f"Policy Group {group}:")
    click.echo("roles|resource group|access")
    click.echo("-|-|-")
    rows = []
    for p in agp:
        policy = Policy(p)
        if dump:
            policy.dump()
        else:
            rows.append(f'{policy.roles()}|{policy.resource_group()}|{policy.resources()}')
    if dump:
        return
    for row in sorted(rows):
        click.echo(row)

def main(dump: Optional[bool] = typer.Option(False), test: Optional[bool] = typer.Option(False), cache: Optional[bool] = typer.Option(False)):
    if not cache:
        runner.clear_cache()

    if dump:
        # generated a markdown table of all resources sorted by group
        for group in ic_iam_access_groups():
            click.echo("")
            table(group["name"], False)
            return
        
    # Generate a list of resources to clean up manually
    clean_resources()

if __name__ == "__main__":
    typer.run(main)
