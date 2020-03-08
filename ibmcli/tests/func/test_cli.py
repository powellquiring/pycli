import ibmcli

def test_cli():
    #ibmcli.uninstall_plugins(True) # dryrun True
    #ibmcli.log_help_commands(True, 'cs') # dryrun True
    #ibmcli.sl_vs_cancel()
    #ibmcli.resource_service_instances_delete()
    ibmcli.docker_ps_a_delete()
    pass