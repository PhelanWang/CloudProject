import json

# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)



'''
return: 
    OK: "{'json_data':{'start_time':start_time,'conf':conf,'has_auth':has_auth}}"
    NO: "{'json_data':{'start_time':start_time,'conf':'None','has_auth':has_auth}}"
        
'''
@agent.entry("vmconf", version="1.0.2")
def set_vmiconf(subtask_id, args):
    import json
    from sec_mem_port import set_vm_libvmi_conf_port
    from lib.node_ta.ta_common import logger
    
    #print '[',args,']','###################',type(args)
    vm_id = ''
    start_time = ''
    try:
        data = json.loads(args)
        print data,type(data)
        vm_id = data['vm_name']
        start_time = data['start_time']
    except Exception,e:
        print 'error for set vmicof to bind agent'
        print str(e)

    #import time
    #time.sleep(100)
    #print 'args ...',vm_id,start_time        
    json_data = set_vm_libvmi_conf_port(vm_id,start_time)
    
    logger.info(json_data)
    
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='set vmiconf',
                      json_data=json_data)

'''
return: 
        json_data = {"process_list": [[4, "System", "866cdc78"], [256, "smss.exe", "878aac48"], ...]}
        json_data = {'process_list':''}
        
'''
@agent.entry("meminfo", version="1.0.2")
def get_mem_info(subtask_id, args):
    from lib.node_ta.ta_common import write_to_file,logger
    from sec_mem_port import get_mem_info_port
    import json
    #print args
    #import time
    #time.sleep(100)
    try:
        vm_id = json.loads(args)['vm_name']
        option_id = json.loads(args)['roption_id']
        id = json.loads(args)['rid']
        confs = json.loads(args)['confs']
        info_data = json.loads(args)['info_data']
        #print json.dumps(confs,indent=4)
        write_to_file('/etc/libvmi.conf', confs)
    except Exception,e:
        print str(e)
        print 'cannot get params'
        
    json_data = get_mem_info_port(vm_id,option_id,id,info_data)
    logger.info(json_data)
    
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get mem info',
                      json_data=json_data)
    
    
    
    

'''
return: 
        json_data = {'is_has_auth':True}
        json_data = {'is_has_auth':False}
        
'''
@agent.entry("vmiauth", version="1.0.2")
def is_has_auth(subtask_id, args):
    from sec_mem_port import is_has_auth_port
    json_data = is_has_auth_port()
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='is has auth',
                      json_data=json_data)
'''
return: 
        json_data = {'is_has_auth':True}
        json_data = {'is_has_auth':False}
        
'''
@agent.entry("setvmiauth", version="1.0.1")
def set_auth(subtask_id, args):
    from sec_mem_port import set_auth_port
    json_data = set_auth_port()
    
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='set auth',
                      json_data=json_data)

'''
return: 
        json_data = {'set_basic':True}
        json_data = {'set_basic':False}
        
'''
@agent.entry("bvmiconf", version="1.0.1")
def set_basic_vmiconf(subtask_id, args):
    from sec_mem_port import set_basic_libvmi_conf_port
    json_data = set_basic_libvmi_conf_port()
    
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='is has auth',
                      json_data=json_data)

'''
return: 
        json_data = {'set_faster':True}
        json_data = {'set_faster':False}
        
'''
@agent.entry("fvmiconf", version="1.0.1")
def set_faster_vmiconf(subtask_id, args):
    from sec_mem_port import set_faster_libvmi_conf_port
    json_data = set_faster_libvmi_conf_port()
    
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='is has auth',
                      json_data=json_data)

'''
return: 
        json_data = {"process_list": [[4, "System", "866cdc78"], [256, "smss.exe", "878aac48"], ...]}
        json_data = {'process_list':''}
        
'''
@agent.entry("getplist", version="1.0.1")
def get_process_list(subtask_id, args):
    from sec_mem_port import get_process_list_port
    vm_id = json.loads(args)['vm_id']
    json_data = get_process_list_port(vm_id)
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get process list',
                      json_data=json_data)

'''
return: 
        json_data = {"module_list": [[4, "System", "866cdc78"], [256, "smss.exe", "878aac48"], ...]}
        json_data = {'module_list':''}
        
'''
@agent.entry("getmlist", version="1.0.1")
def get_module_list(subtask_id, args):
    from sec_mem_port import get_module_list_port
    vm_id = json.loads(args)['vm_id']
    json_data = get_module_list_port(vm_id)
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='get module list',
                      json_data=json_data)
    

# Execute this while run this agent file directly
if not is_load_external():
#     get_
    # Run agent
    # agent.run()
    pass
