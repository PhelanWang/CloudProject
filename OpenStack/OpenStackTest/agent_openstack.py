# coding: utf-8
import json


def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)


@agent.entry("component_encryption", version="1.0.1")
def component_encryption(subtask_id, args):
    from openstack_encryption.compoment_encryption import test_component_encryption
    data, token = test_component_encryption()
    result = '获取到OpenStack组件间的通信数据，列出部分数据如下：\n'+data+token
    brief = '从获取的数据中能看到，OpenStack组件间通信数据未加密，但是使用了token进行权限验证。\n'
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='',
                      detail=brief.replace('\n', '</br>'),
                      json_data=result.replace('\n', '</br>'))


@agent.entry("openstack_flaw_scan", version="1.0.1")
def openstack_flaw_scan(subtask_id, args):
    import sqlite3
    json_data = []
    conn = sqlite3.connect('data/openstack_flaw.db')
    c = conn.cursor()
    result = c.execute('SELECT TITLE, DETAIL, IMPACT_PRODUCT FROM FLAW_TABLE').fetchall()
    for line in result:
        item = {}
        item['bugName'] = line[0]
        item['bugInfo'] = line[1]
        json_data.append(item)
    if json_data == []:
        detail = '在此系统中没有发现OpenStack漏洞'
        json_data = [{'bugName': '无', 'bugInfo': '无'}]
    else:
        detail = 'OpenStack漏洞：根据系统环境，扫描系统列出系统中可能存在的OpenStack漏洞'

    agent.post_report(subtask_id,
                      severity=1,
                      result=0,
                      brief='OpenStack',
                      detail=detail,
                      json_data=json_data)


# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    agent.run()
    # openstack_flaw_scan(0, 0)
