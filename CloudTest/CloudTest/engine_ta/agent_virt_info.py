
# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

# OK
@agent.entry("engine_status", version="1.0.2")
def engine_status(subtask_id, args):
    from info.virt_info import get_engine_status
    json_data = {}
    print 'enigne status info ...'
    
    status=get_engine_status()
    
    if status:
        json_data['status'] = 'up'
    else:
        json_data['status'] = 'down'
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get eingie status ......',
                      json_data=json_data)

# OK
@agent.entry("hosts", version="1.0.2")
def hosts(subtask_id, args):
    from info.virt_info import get_hosts
    json_data = {}
    print 'enigne status info ...'
    
    hosts = get_hosts()
    
    if hosts:
        json_data['hosts'] = hosts
    else:
        json_data['hosts'] = []
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get eingie status ......',
                      json_data=json_data)

# OK
@agent.entry("disk_enc", version="1.0.2")
def disk_enc(subtask_id, args):
    from info.virt_info import get_vm_disks_for_enc
    json_data = {}
    print 'enigne status info ...'
    
    lst_vm_disks = get_vm_disks_for_enc()
    
    if lst_vm_disks:
        json_data['lst_vm_disks'] = lst_vm_disks
    else:
        json_data['lst_vm_disks'] = []
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get vm list for mem ......',
                      json_data=json_data)

# OK
@agent.entry("vm_mem", version="1.0.2")
def vm_mem(subtask_id, args):
    from info.virt_info import get_vms_for_mem
    json_data = {}
    print 'enigne status info ...'
    
    lst_vm_mem = get_vms_for_mem()
    
    if lst_vm_mem:
        json_data['lst_vm_mem'] = lst_vm_mem
    else:
        json_data['lst_vm_mem'] = []
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get vm list for mem ......',
                      json_data=json_data)


# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    agent.run()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
