__author__ = 'Henry'

# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

@agent.instrusive
def get_vm_hosts(args):
    from info.virt_info import get_vm_mac_ip

    try:
        vm_hosts = get_vm_mac_ip()
        if vm_hosts:
            data = []
            for vm_host in vm_hosts:
                if vm_host and len(vm_host) > 3:
                    data.append(vm_host[3])
            return {'data': data}
    except BaseException, e:
        print 'get_vm_hosts(): ' + e.message
    return {'data': []}

# Execute this while run this agent file directly
if not is_load_external():
#     print get_vm_hosts(0)
    # Run agent
    agent.run()
