# coding: utf-8
from time import sleep
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

# Register function "my_openvas" on service "openvas"
# OK
# 格式修改完成
@agent.entry("spice", version="1.0.1")
def spice(subtask_id, args):
    # Post report to switch server:
    # agent.post_report(subtask_id, severity, result, brief, detail, json_data)
    import os, time, ConfigParser
    from spice_vnc.format_data import get_format_data
    conf = ConfigParser.ConfigParser()
    conf.read('spice_vnc.conf')
    port = conf.get('SPICE', 'port', '5900')
    cmd = 'tshark -i any -n -f "src port '+port+'" -d "tcp.port=='+port+',vnc" -a duration:60 -w data.cap'
    print 'please wait 2 mins,spice is testing...'
    print cmd
    os.system(cmd)
    #time.sleep(120)
    os.system('hexdump -C data.cap > spice.txt')
    #print 'please wait 5 mins,spice is testing...'
    #time.sleep(120)
    print 'begin to anaylyse...'
    #os.system('chmod 777 data.cap')
    #result=os.popen('hexdump -C data.cap')
    file = open('spice.txt')
    result = file.read()
    file.close()
    result = get_format_data(result, 15)
    #print result
    os.system('rm -rf data.cap')
    # json_data is default as None
    detail = 'SPICE(Simple Protocol for Independent Computing Environments)\n' \
             '是redhat开发的开源的专门的桌面虚拟化数据传输协议。\n' \
             '本次测试在使用SPICE协议的云平台环境中获取通信数据。\n' \
             '获取的数据包括数据ID信息，数据的十六进制格式，数据的内容。\n' \
             '从抓取的信息中表明该协议传输的数据是加密的。\n'
    for line in result:
        print line
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='SPICE',
                      detail=detail.replace('\n', '</br>'),
                      json_data=result)

# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    agent.run()
    # os.system('bash spice/run.sh')
    # spice(0, 0)
    
