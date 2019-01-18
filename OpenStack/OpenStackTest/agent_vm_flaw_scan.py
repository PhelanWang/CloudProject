# coding: utf-8

def is_load_external():
    return globals().has_key('AGENT_LOADER')


if not is_load_external():
    from lib.agent.ctest import SwitchAgent
    agent = SwitchAgent(__name__)


@agent.entry("vm_flaw_scan", version='1.0.1')
def vm_flaw_scan(subtask_id, args):
    from access_detection.vm_access_controll_detection import get_vm_infor, version_comapre
    import sqlite3, re, time
    # args = {'path': '/root/PycharmProjects/96d9b1b5-2f45-4baf-8462-5a166c87a3bb',
    #         'name': '96d9b1b5-2f45-4baf-8462-5a166c87a3bb'}
    json_data = []
    time.sleep(10)
    infor, version = get_vm_infor(args)
    if (not infor) or (not version):
        brief = '测试功能首先将虚拟机磁盘挂载，获取虚拟机系统信息。\n' \
                '然后扫描vce，oval漏洞信息库，列出漏洞名称和漏洞信息。\n' \
                '虚拟机中未发现漏洞。'
        json_data = [{'bugName': '无', 'bugInfo': '无'}]
    else:
        brief = '测试功能首先将虚拟机磁盘挂载，获取虚拟机系统信息。\n' \
                '然后扫描vce，oval漏洞信息库，列出漏洞名称和漏洞信息。\n' \
                '获取虚拟机系统信息:\n'+infor+'\n虚拟机中可能存在的漏洞如下：'
        version = '.'.join(version.split('.')[:2])
        conn = sqlite3.connect('data/vm_flaw.db')
        c = conn.cursor()
        result = c.execute('SELECT TITLE, DETAIL, IMPACT_PRODUCT FROM FLAW_TABLE').fetchall()
        for line in result:
            item = {}
            item['bugName'] = line[0]
            item['bugInfo'] = line[1]
            if 'Linux Kernel' in line[2]:
                flaw_version = re.findall(r'([0-9].[0-9])', line[2])
                if flaw_version and version_comapre(flaw_version[0], version):
                    json_data.append(item)
        if len(json_data) == 0:
            json_data = [{'bugName': '无', 'bugInfo': '无'}]

    # print json_data
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='',
                      detail=brief.replace('\n', '</br>'),
                      json_data=json_data)


if not is_load_external():
    # my_unsecurity_service_testing(0, 0)
    # Run agent
    agent.run()
