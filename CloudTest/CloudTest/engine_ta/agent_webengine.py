# coding: utf-8
from boto import log
__author__ = 'pushpin'
def is_load_external():
    return globals().has_key('AGENT_LOADER')

if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

# Register function "my_enginecheck" on service "enginecheck"
@agent.entry("webengine", version='1.0.1')
def my_webengine(subtask_id, args):
    from encryption.enginecheck import enginecheck
    engine_ip = '127.0.0.1'
    print 'startup webengine while the engine ip address is %s ' % engine_ip if engine_ip else 'Nothing'
    logInfo = ""

    my_enginecheck = enginecheck(engine_ip)
    checklist = my_enginecheck.engine_check()
    my_enginecheck.tools_version()
    logfile = '.info%s' % engine_ip
    logio = open(logfile)
    toolsversion = None
    try:
        for lines in logio:
            if lines.find("OpenSSL") != -1:
                toolsversion = lines
            logInfo += lines
    except Exception, e:
        pass
    finally:
        logio.close()

    brief = "通过测试VDSM云平台引擎服务，检测结果为模块间的通信是未加密的。\n"
    detail = brief + "\n因为 http 没有加密。"
    for items in checklist:
        if items[0] == 443 or items[0] == 8443 or items[1] == "https":
            brief = '通过测试VDSM云平台引擎服务，检测结果为模块间的通信是加密的。\n' \
                    '测试列出了协议和端口，数字摘要算法，服务证书。\n'
            detail = '平台传输层使用协议: '+items[1]+'， 端口: '+str(items[0])+'\n'
            detail += 'VDSM程序模块间的安全传输协议为：\n'+items[3][0]+'\n'
            detail += '协议间使用的公钥长度为： '+items[4][0]+'\n'
            detail += 'VDSM使用的数字摘要算法为：\n'+items[6][0]+'\n'
            detail += 'VDSM使用的服务证书为:\n'+items[5][0]

    print(brief)
    print(detail)
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief=brief,
                      detail=brief.replace('\n', '</br>'),
                      json_data=detail.replace('\n', '</br>'))

# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    agent.run()
    # args = {}
    # args['ip'] = "localhost"
    # my_webengine(0, args)
