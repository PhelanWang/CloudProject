# -*- coding: utf-8 -*-
#系统执行execfile时第一次运行该模块
from numpy.dual import det

__author__ = 'Henry'

def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)


# 这里agent是SwitchAgent的实例，运行该类的entry函数
@agent.entry("mmount", version="1.0.2")
def mmount_test(subtask_id,args):
    from virus_scan.mount import Mounter
    disk_path = ''
    disk_name = ''
    disk_type = ''
    print args
    try:
        disk_path = args["path"]
        disk_name = args["name"]
        # disk_type = args["type"]
    except:
        print "can't get args!"
        
    mt = Mounter(disk_path, disk_name)
    # print 'start mounting...'
    #mount = mt.mount()
    report = mt.getReport()
    rpt=''
    detail=''
    brief=''
    
    #print report
    
    if(report==False):
            rpt=u'启动虚拟机失败，该磁盘不可引导或未初始化'
            brief='start vm failed'
            detail=rpt
    else:
        brief ='start vm success'
        detail=report
        rpt=report
    print 'rpt'
    print rpt
    agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief=brief,
                          detail=detail,
                          json_data={'mm_result':rpt})


# Execute this while run this agent file directly
if not is_load_external():
#     args = {}
#     args["path"] = '/root/share/cb7e72a4-b396-4e24-bbb2-717e0bf62e49/images/cdab97a6-da5e-4103-aa24-9d9cf84440e3/7b2465ac-d3b2-4a79-b384-2c73bfb27521'
#     args["name"]  = '7b2465ac-d3b2-4a79-b384-2c73bfb27521'
#     mmount_test(0, args)
    # Run agent
    agent.run()
