# -*- coding: utf-8 -*-
__author__ = 'root'
import time

def is_load_external():
    return globals().has_key("AGENT_LOADER")

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

# 格式修改完成
@agent.entry("vnic_testing",version="1.0.1")
def vnic_analysis(subtask_id, args):
    from vnic.vnic_analy import VnicTest
    print "vnic test shell run!"
    detail = '虚拟机进行网络通信时，可以直接使用宿主机中的vhost模块。\n' \
             '通过该模块将网络数据发送给宿主机，再由宿主机将数据发送，接收过程类似。\n'\
             '本测试功能在vhost模块中将虚拟机的网络数据旁路到宿主机中，然后对导出的原始数据进行分析。\n'
    rpt = {
            "detail": "未能旁路此网卡数据，请按照测试步骤操作!",
            "result": "未能旁路此网卡数据，请按照测试步骤操作!"
        }
    vt = VnicTest('qemu-kvm', 'vhost')
    try:
        # 关闭所有虚拟机进程
        vt.shutdown()
        if vt.begin():
            rpt = vt.stop()
    except:
        rpt["brief"] = "未能旁路此网卡数据，测试时出现位置错误，请重新运行测试功能!\n"
        rpt["result"]= "未能旁路此网卡数据，测试时出现位置错误，请重新运行测试功能!\n"
    print rpt['detail']
    print rpt['result']
    agent.post_report(subtask_id,
                      severity=1,
                      result=1,
                      brief=None,
                      detail=(detail + rpt['detail']).replace('\n', '</br>'),
                      json_data=rpt['result'].replace('\n', '</br>'))

# Execute this while run this agent file directly
if not is_load_external():
    # vnic_analysis(0, 0)
    # Run agent
    agent.run()
    
