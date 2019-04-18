# -*- coding:utf-8 -*-



# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')
# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent=SwitchAgent(__name__)


# Register function "my_openvas" on service "openvas"

# OJBK
# 没有抓到数据
@agent.entry("unsecurity_service_testing", version="1.0.1")
def my_unsecurity_service_testing(subtask_id,args):
    from lib.agent.ctest import SwitchAgent
    import threading
    from threading import Thread
    from sec_network import client as cli
    from sec_network import unsecurity_service as unsecurity
    import time, os
    from sec_network.pyTimer import Pysettimer

    # Get value of global K-V database item "engine-ip". see get_global(), set_global()
    #engine_ip=agent.get_global("engine-ip")
    pid = os.popen("lsof -i:8001 | grep python | awk '{print $2}'").read().strip(' \n')
    if pid:
        os.system('kill -9 '+pid)
#     client=Pysettimer(cli.sendmessage, "Hello World")
    os.system('python vmnet/server_python2.py localhost:8001 &')
    #---\
    capture = Pysettimer(unsecurity.capture, 'test')
    #---/
    # client.setDaemon(True)
    # client.start()
    # time.sleep(10)
    #----\
    capture.start()
    capture.join()
    #----/
    # Post report to switch server:
    # agent.post_report(subtask_id, severity, result, brief, detail, json_data)
    # json_data is default as None
    detail = '本测试功能通过IM(InstantMessaging)实时通信程序测试虚拟机网络的联通性。\n' \
             '测试时在虚拟机中部署客户端程序，在宿主机中部署服务端程序，然后通信。\n' \
             '测试尝试将通信数据抓取并分析。\n'
    if(unsecurity.get_captured()):
        with open('sec_network/packlog/filterpackudp', 'r') as file:
            data = file.readlines()
            data = reduce(lambda a, b: a + b, data[:min(10, len(data))], '')
            print data
        print unsecurity.getfilterpackupd()
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='String Match Successful! ',
                          detail=detail + '抓取到通信数据，虚拟机网络联通的，测试程序传输的UDP数据未加密。\n'.replace('\n', '</br>'),
                          json_data=data.replace('\n', '</br>'))
    else:
        print 'else'
        agent.post_report(subtask_id,
                          severity=1,
                          result=1,
                          brief='String Match failed',
                          detail=detail + '测试中未抓取到数据，虚拟机网络不联通或者操作步骤不正确。\n'.replace('\n', '</br>'),
                          json_data='未获取到通信数据。\n'.replace('\n', '</br>'))


# Execute this while run this agent file directly
if not is_load_external():
    # my_unsecurity_service_testing(0, 0)
    # Run agent
    agent.run()
# 在虚拟机中启动 vmnet 下 client_python2.py localhost:8001