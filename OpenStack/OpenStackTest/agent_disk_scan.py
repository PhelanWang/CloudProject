# -*- coding: utf-8 -*-

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
# 扫描磁盘，并比较关键字，检测磁盘是否加密
# nfs 镜像文件路径
# 格式检测完成，返回内容修改完成
# args {'path': '/root/share/cb7e72a4-b396-4e24-bbb2-717e0bf62e49/images/cdab97a6-da5e-4103-aa24-9d9cf84440e3/7b2465ac-d3b2-4a79-b384-2c73bfb27521'})
@agent.entry("disk_scan", version="1.0.1")
def my_disk_scan(subtask_id, args):
    from sec_storage.disk_scan import get_vm_disk_size,symbol_scan
    import time

    time.sleep(15)
    vm_disk_path = args["path"]
    vm_disk_size = int(get_vm_disk_size(vm_disk_path))
    report = symbol_scan(vm_disk_path, vm_disk_size)
    if report == "磁盘错误, 扫描出现未指定错误!" or report == "磁盘错误, 无法获取磁盘空间信息!":
        detail = report + "本次磁盘扫描失败，请检测磁盘路径是否正确。"
    else:
        detail = report['result']
        report = report['detail']

    print detail
    print report
    agent.post_report(subtask_id,
                      severity=1,
                      result=0,
                      brief='result of disk_scan',
                      detail=detail.replace('\n', '</br>'),
                      json_data=report.replace('\n', '</br>'))

# OK
# 删除文件，并检测是否擦除
# args {'path': '/root/share/cb7e72a4-b396-4e24-bbb2-717e0bf62e49/images/cdab97a6-da5e-4103-aa24-9d9cf84440e3/7b2465ac-d3b2-4a79-b384-2c73bfb27521'})
# 格式修改完成
# 修改到engine中
# 格式修改完成，返回内容修改完成
@agent.entry("erase_scan", version="1.0.1")
def my_erase_scan(subtask_id, args):
    from sec_storage.disk_erase_detect import get_total_save, do_erase_scan
    import os

    print 'startup erase_scan'
    args = {'path': os.getcwd()+'/sec_storage/test-disk'}
    print args['path']
    disk_path = args['path']

    detail = '磁盘擦出检测检测云平台上将虚拟磁盘擦除时，是否能够根据磁盘的块号读取还原磁盘内容。\n' \
             '虚拟机磁盘一般为RAW格式或者QCOW2格式，可以使用文件系统管理工具对其进行扫描。\n'

    result = get_total_save(disk_path)
    if result == "ERROR":
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='',
                          detail=(detail+'进行磁盘扫描失败。\n').replace('\n', '</br>'),
                          json_data="进行指定磁盘扫描失败，请检查给定路径是否正确。\n".replace('\n', '</br>'))
        return
    os.system('cp ' + disk_path + ' ' + disk_path + '1')
    os.system('rm ' + disk_path)
    report = do_erase_scan()
    os.system('mv ' + disk_path + '1' + ' ' + disk_path)
    if not report:
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail=(detail+'进行磁盘扫描失败。\n').replace('\n', '</br>'),
                          json_data="进行指定磁盘扫描失败，请检查给定路径是否正确。\n".replace('\n', '</br>'))
    else:
        print 'report', report['result'], 'detail', report['detail']
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail=(detail+report['detail']).replace('\n', '</br>'),
                          json_data=report['result'].replace('\n', '</br>'))


# 格式修改完成，返回内容修改完成
@agent.entry("cross_memory", version="1.0.1")
def my_cross_memory(subtask_id, args):
    import os
    from memory_scan.memory_cross import memory_scan
    (report, state) = memory_scan()
    if not state:
        detail = '本次测试获取虚拟机进程空间的内存地址，并进行检测。\n'\
                 '检测运行的虚拟机之间是否有交叉的内存页面，若发现交叉内存页面，则将部分页面地址列出来。\n' \
                 '本次运行测试功能失败!'
    else:
        detail = '本次测试获取虚拟机进程空间的内存地址，并进行检测。\n'\
                 '隔离检测运行的虚拟机之间是否有交叉的内存页面，若发现交叉内存页面，则将部分页面地址列出来。\n' \
                 '本次运行测试功能成功!'
        if report == []:
            detail += '\n测试中未发现交叉内存页面!'
        else:
            detail += '\n测试中发现交叉内存页面，显示部分交叉页面地址如下:\n' \
                      '若要显示所有交叉的内存页面地址，查看节点上文件，路径为：' + os.getcwd() + '/memory_scan/umuery/v_result'.replace('\n', '</br>')
    print detail, '\n', report
    agent.post_report(subtask_id,
                        severity=1,
                        result=0,
                        brief='done',
                        detail=detail.replace('\n', '</br>'),
                        json_data=report.replace('\n', '</br>'))


# 格式修改完成
@agent.entry("virtual_disk_scan", version="1.0.1")
def my_vdisk_scan(subtask_id, args):
    from vdisk.vdis_scan import virtual_disk_scan

    args = {}
    args['keyword'] = ['ovirt-test', 'cloud-platforms', 'virtual-scan', 'data-isolate']

    data = virtual_disk_scan(args)

    detail = 'KVM使用virtio半虚拟化驱动，虚拟机中的前端模块virtio_blk将虚拟机的文件内容通过virtio-ring将数据写入到后端。\n' \
             '本测试功能在virtio-ring处，把需要写入到磁盘的数据旁路到宿主机上分析，提取出关键字相关内容\n' \
             '虚拟机磁盘隔离测试，启动虚拟机后在任意文件中写入内容，如果如果内容中有' + reduce(lambda a, b: a+', '+b, args['keyword'], '') + \
             '等关键字，将会把相关的数据旁路出来。\n'
    if data == '':
        detail += '本次测试未在旁路的数据中发现指定关键字。'
    else:
        detail += '本次测试在旁路的数据中发现指定关键字，旁路出的关键字内容如下：'
    print data
    agent.post_report(subtask_id,
                      severity=1,
                      result=0,
                      brief='',
                      detail=detail.replace('\n', '</br>'),
                      json_data=data.replace('\n', '</br>'))


# Execute this while run this agent file directly
if not is_load_external():
    # Run agent
    agent.run()

