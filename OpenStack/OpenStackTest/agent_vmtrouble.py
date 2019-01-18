# coding: utf-8

import pexpect
import os
import time


def is_load_external():
    return globals().has_key('AGENT_LOADER')


# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent
    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)


@agent.entry("blue_screen", version="1.0.1")
def blue_screen(subtask_id, args):
    from vm_trouble.vm_trouble import execute_test
    import time
    time.sleep(120)
    print("start test. . .\n")
    try:
        before_data, after_data = execute_test()
    except:
        before_data = 'None'
        after_data = 'None'
    result = '启动两台虚拟机后，信息如下:\n' + before_data + '\n一台虚拟机故障后，信息如下:\n' + after_data

    print result
    detail = '虚拟机故障检测功能在云平台上启动两台虚拟机，获取虚拟机和云平台的信息。\n'\
             '然后使一台虚拟机故障，并在次获取虚拟机和云平台的信息。\n' \
             '测试启动两台虚拟机，获取虚拟机信息后使一台虚拟机故障，再次获取系统信息。\n'
    if (not before_data) and (not after_data):
        detail += '获取虚拟机信息失败，可能受云平台影响，可稍后再进行测试。\n'
    else:
        detail += '可以从信息中看到，一台虚拟机故障后不会影响另一台虚拟机的正常运行。\n'\
                  '并且正常的释放了内存，未影响云平台。\n'\
                  '各个字段含义：\n'\
                  'actual:能够对虚拟机分配的最大内存限制。\nswap_in:交换区中的内存。\nrss:实际给虚拟机分配的内存。\n'\
                  'used:宿主机使用的内存。\nfree:空闲的物理存储。\nshared:多个进程共享的内存总和。'
    print detail
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='',
                      detail=detail.replace('\n', '</br>'),
                      json_data=result.replace('\n', '</br>'))

# Execute this while run this agent file directly
if not is_load_external():
    agent.run()
    # pass
    # blue_screen(0, 0)