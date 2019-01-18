# coding: utf-8
__author__ = 'pushpin'
def is_load_external():
    return globals().has_key('AGENT_LOADER')

if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

# Register function "my_enginecheck" on service "enginecheck"

# OJBK 需要先启动encryption下的nfsagent.py
# bash: dumpscript.sh: 没有那个文件或目录
@agent.entry("nfs", version='1.0.1')
def my_nfs(subtask_id,args):
    from encryption.nfscheck import entryfunction
    nfsip = args['ip']
    filename = args['test_filename']
    result = entryfunction(nfsip, filename)
    toolsversion = "TShark 1.10.3 (SVN Rev Unknown from unknown)"

    if result[0]:
        conclusion = "The connection with NFS service is encrypted."
        brief = "The NFS service is safe."
        detail = "The data flow of file synchronization is encrypted."
    else:
        conclusion = "The connection with NFS service is not encrypted"
        brief = "The NFS service is not safe."
        detail = "The data flow of file synchronization is not encrypted."
        
        
    print 'conclusion: ', conclusion, ' brife:', brief, ' detail: ', detail
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief=brief,
                      detail=detail,
                      json_data={"conclusion": conclusion,
                                 "nfsip":nfsip,
                                 "tools_version": toolsversion,
                                 "proof": result[1]
                                 }
                      )
    
# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    args = {}
    args['ip'] = '192.168.1.113'
    args['test_filename'] = 'abc'
    my_nfs(0, args)
    agent.run()
    
    
    
    
    
    
    
    
    
    
