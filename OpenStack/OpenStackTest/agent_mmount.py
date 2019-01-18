# -*- coding: utf-8 -*-
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


# Register function "my_openvas" on service "openvas"


# OK
# 对于同一个磁盘mount两个会出错，尝试只启动一台
# 格式修改完成，返回内容修改完成
@agent.entry("mmount", version="1.0.1")
def mmount_test(subtask_id, args):
    from virus_scan.mount import Mounter
    import time
    time.sleep(60)
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
    # mount = mt.mount()
    report = mt.getReport()
    mt.killid()
    rpt = ''
    detail = ''
    brief = ''
    print '---------------'
    print report
    print '---------------'

    if report == False:
        detail = '云平台创建的虚拟机磁盘一般使用的是RAW或者QCOW2格式。\n' \
                 '对于同一个虚拟机磁盘使用是互斥的，即每次只能有一个进行将虚拟磁盘挂载。\n' \
                 '磁盘多重挂载测试对于同一个虚拟磁盘，是否能够同时挂载到多个虚拟机。\n' \
                 '测试中尝试对一个磁盘进行多重挂载。\n' \
                 '本次测试失败，给定磁盘不可引导或未初始化。\n'
    else:
        detail = '云平台创建的虚拟机磁盘一般使用的是RAW或者QCOW2格式。\n' \
                 '对于同一个虚拟机磁盘使用是互斥的，即每次只能有一个进行将虚拟磁盘挂载。\n'\
                 '磁盘多重挂载测试对于同一个虚拟磁盘，是否能够同时挂载到多个虚拟机。\n' \
                 '测试中尝试对一个磁盘进行多重挂载。\n' \
                 '本次测试成功，测试结果如下：\n'

    print '----'
    print detail
    print '----'
    agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief=brief,
                          detail=detail.replace('\n', '</br>'),
                          json_data=report.replace('\n', '</br>'))


# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    args = {}
    args["path"] = '/root/data/72fb40f0-f2c1-4edc-a81c-739c1205f208/images/c88f8df3-3f0d-4587-8be1-cc21f526c3a0/' \
                   '1309ea24-0181-424b-a147-0cc866633428'
    args["name"] = '1309ea24-0181-424b-a147-0cc866633428'
    # mmount_test(0, args)
    agent.run()
