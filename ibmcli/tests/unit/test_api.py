import ibmcli
import re
def test_plugin_list():
    example_output = """Listing installed plug-ins...

Plugin Name                                 Version   Status   
dev                                         2.4.0
cloud-functions/wsk/functions/fn            1.0.35
container-service/kubernetes-service        0.4.38    Update Available"""

    plugins = ibmcli.plugin_list(example_output)
    assert(len(plugins) == 3)
    assert(plugins[0].name == 'dev')
    assert(plugins[0].aliases == [])
    assert(plugins[0].version == '2.4.0')
    assert(plugins[0].status == '')
    assert(plugins[1].name == 'cloud-functions')
    assert(plugins[1].aliases == ['wsk', 'functions', 'fn'])
    assert(plugins[1].version == '1.0.35')
    assert(plugins[1].status == '')
    assert(plugins[2].status == 'Update Available')

def test_plugin_repo_plugin():
    example_output = """Getting plug-ins from all repositories...

Repository: IBM Cloud
Status             Name                                        Versions                       Description   
Update Available   container-service/kubernetes-service        0,0.1...                       yada zada
Not Installed      logging-cli                                 1.0.8, 1.0.7, 1.0.6...         [Deprecated] Manage Log Analysis Service.
Installed          tke                                         0.0.11, 0.0.9, 0.0.7...        Manage the master key of Cloud HSMs from Hyper Protect Crypto service

Use ibmcloud plugin update PLUGIN_NAME -r REPO_NAME to update a plugin from a repo.
"""

    plugins = ibmcli.plugin_repo_plugins(example_output)
    assert(len(plugins) == 3)
    p = plugins[0]
    assert((p.status, p.name, p.aliases, p.version, p.description) == ('Update Available', 'container-service', ['kubernetes-service'], '0,0.1...', 'yada zada'))

def the_test_string():
    ret_string = """ 
NAME:
        ibmcloud ks - Manage IBM Cloud Kubernetes Service clusters.
USAGE:
        ibmcloud ks command [arguments...] [command options]

COMMANDS:

Cluster Management Commands:
    cluster       View and modify cluster and cluster service settings.
    worker        View and modify worker nodes for a cluster.
    worker-pool   View and modify worker pools for a cluster.
    zone          List availability zones and modify the zones attached to a worker pool.

Cluster Components Commands:
    alb                  View and configure an Ingress application load balancer (ALB).
    key-protect-enable   [Beta] Enable Key Protect as a key management service (KMS) in your cluster to encrypt your secrets.
    logging              Forward logs from your cluster.
    nlb-dns              Create and manage host names for network load balancer (NLB) IP addresses in a cluster and health check monitors for host names.
    va                   View a detailed vulnerability assessment report for a container that runs in a cluster.
    webhook-create       Register a webhook in a cluster.

Account Management Commands:
    api-key             View information about the API key for a cluster or reset it to a new key.
    credential          Set and unset credentials that allow you to access the IBM Cloud classic infrastructure portfolio through your IBM Cloud account.
    infra-permissions   View information about infrastructure permissions that allow you to access the IBM Cloud classic infrastructure portfolio through your IBM Cloud account.
    subnets             List available portable subnets in your IBM Cloud infrastructure account.
    vlan                List public and private VLANs for a zone and view the VLAN spanning status.
    vpcs                List all VPCs in the targeted resource group. If no resource group is targeted, then all VPCs in the account are listed.

Informational Commands:
    addon-versions           List supported versions for managed add-ons in IBM Cloud Kubernetes Service.
    flavors, machine-types   List available flavors for a zone. Flavors determine how much virtual CPU, memory, and disk space is available to each worker node.
    kube-versions            [Deprecated] List the Kubernetes versions currently supported by IBM Cloud.
    messages                 View the current user messages.
    supported-locations      List supported IBM Cloud Kubernetes Service locations.
    versions                 List all the container platform versions that are available for IBM Cloud Kubernetes Service clusters.

Configuration Commands:
    api    View or set the API endpoint and API version for the service.
    init   Initialize the Kubernetes Service plug-in and get authentication tokens.

Other Commands:
    script   Rewrite scripts that call IBM Cloud Kubernetes Service plug-in commands. Legacy-structured commands are replaced with beta-structured commands.

Enter 'ibmcloud ks help [command]' for more information about a command.


ENVIRONMENT VARIABLES:
   IKS_BETA_VERSION=0.4    Enable beta command structure. The default behavior is '0.4'.
                             Set to '0.4' to show beta command structure and run commands in either structure.
                             Set to '1.0' to show beta command structure and run commands in the beta structure. IMPORTANT: The changes to command behavior and syntax in version 1.0 are not backwards compatible. For a summary of the changes, see http://ibm.biz/iks-cli-v1
"""
    ret_expected = [
    'cluster',
    'worker',
    'worker-pool',
    'zone',
    'alb',
    'key-protect-enable',
    'logging',
    'nlb-dns',
    'va',
    'webhook-create',
    'api-key',
    'credential',
    'infra-permissions',
    'subnets',
    'vlan',
    'vpcs',
    'addon-versions',
    'flavors',
    'kube-versions',
    'messages',
    'supported-locations',
    'versions',
    'api',
    'init',
    'script',
    ]
    return(ret_string, ret_expected)

def test_commands():
    # stdout = log_help_command(command, **kwargs)
    (stdout, expected) = the_test_string()
    ret = ibmcli.get_commands_from_string(['ibmcloud','cs'], stdout)
    assert(expected == ret)

def test_id_list_from_editor_output():
    bs="""id         hostname                          domain        cpu   memory   public_ip        private_ip       datacenter   action   
92131842   aaa-classic-vm                    howto.cloud   1     1024     169.62.198.232   10.220.134.76    dal13           
92115960   ais-the-lonliest-classic-vm       howto.cloud   1     1024     169.62.198.230   10.220.134.75    dal13           """
    ret = ibmcli.id_list_from_editor_output(bs)
    assert(len(ret) == 2)
    assert(ret[0] == "92131842")
    assert(ret[1] == "92115960")

def test_is_command():
    bs="""Listing images for generation 1 compute in region us-south under account Powell Quiring's Account as user pquiring@us.ibm.com...
ID                                     Name                              Status      OS                                                            Arch    File size(GB)   Created                         Visibility   Resource group
0f99220d-be3a-4d68-b71f-a4df11c9ad2d   ubuntu-base-00                    available   centos-7-amd64(7.x - Minimal Install)                         amd64   5               2019-10-16T15:34:51.179-07:00   private      1dc8536cb06d4f07b49562a0c69e747b
1c2837ed-3a39-4195-b172-e289aa2e2838   ubuntu1804                        available   ubuntu-18-04-amd64(18.04 LTS Bionic Beaver Minimal Install)   amd64   2               2019-10-24T16:25:30.259-07:00   private      1dc8536cb06d4f07b49562a0c69e747b"""
    ret = ibmcli.id_list_from_editor_output(bs, header_lines=2)
    assert(len(ret) == 2)

def test_parts_matching_headers():
    bs="""Name                                         Location   State    Type
atjjj35561-kp-data                           us-south   active   service_instance
keyprotect 08-02                             us-south   active   service_instance"""
    parts = [part for part in ibmcli.parts_matching_headers(bs, 'Name', 'Location', 'State', 'Type')]
    assert(len(parts) == 2)
    assert(parts[1][0] == 'keyprotect 08-02')

from pathlib import Path
def test_json_csv_empty():
    assert(ibmcli.csv_file_str_from_json('[]', ['name']) == None)

def test_json_csv():
    for test_plan in [
        ['kp-list.json', ['name', 'creationDate', 'type', 'id'], 'id', ["2b61ea55-bacf-453e-a61b-b7c7bf5405fd"]],
        ['resource-service-instrances.json', ['name', 'region' 'type', 'subtype', 'id'], "id", ["id 1", "id 2"]],
    ]:
        json_csv(*test_plan)

def json_csv(file_name, fieldnames, id, expected_results):
    json_file = __file__
    py_path = Path(json_file)
    json_path = py_path.with_name(file_name)
    with json_path.open() as content_file:
        json_s = content_file.read()
        csv_file_str = ibmcli.csv_file_str_from_json(json_s, fieldnames)
        ids = ibmcli.ids_from_csv_file_str(csv_file_str, fieldnames, id)
        assert(ids == expected_results)