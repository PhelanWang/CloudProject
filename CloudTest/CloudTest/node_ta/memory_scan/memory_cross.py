# coding=utf-8
'''
Created on Apr 22, 2016

@author: root
'''
# from sos.plugins import sysvipc
# import MySQLdb
'''
孙浩实现
'''
from umuery.text import find_same
################################################################################################
def getallvm_mem():
    import os, sys, time
    child = os.popen("virsh list")
    r = child.read()
    output = open("/getall.txt", "w")
    output.writelines(r)
    output.close()
    list = {}
    file1 = open("/getall.txt", "r")
    lines = file1.readlines() 
    i = 2
    while(i < len(lines) - 1):
        lin = lines[i]
        s_id = lin[1:6]
        s_name = lin[7:]
        list.setdefault(s_id, s_name)
        i = i + 1
    file2 = open("/getall.txt", "w")
    file2.truncate()
    file2.close()
    report = "虚拟机列表信息如下:<br>"
    for id in list:
        theid = int(id)
        childs = os.popen("virsh dommemstat %s" % theid)
        report += "虚拟机名称:  "
        report += list[id]
        report += " 内存信息:"
        report += childs.read()
        report += "<br>"
    return report


def memory_scan():
    import os
    import sys
    reload(sys)
    print 'start memory_scan'
    strs = os.popen("pidof 'qemu-kvm'").read()
    strq = strs.strip('\n ').split(' ')
    if len(strq) < 2 :
        thereport = "测试节点中不存在启动的虚拟机或者启动虚拟机的数量小于2台，无法进行测试!"
        return (thereport, False)
        # 这里将thereport写入数据库
    else:
        # 切换工作目录
        current_path = os.getcwd()
        print current_path
        os.chdir(current_path + "/memory_scan/umuery")
        os.system("rm -rf v_result")
        thereport = memory_scan_details()
        os.chdir("../../../")
    return (thereport, True)


def memory_scan_details():
    print "this is memory_scan_details"
    import os
    report_content = []

    current_path = os.getcwd()
    path = [current_path]
    qemu_ids_str = os.popen("pidof 'qemu-kvm'").read()

    # 获取所有虚拟机进程的ID
    qemu_ids = qemu_ids_str.split("\n")[0].split(" ")

    # 选取第一个虚拟机进程和其他虚拟机进程进行内存比较
    for v_id2 in qemu_ids[1:]:
        report_lines = memory_scan_batch(path, int(qemu_ids[0]), int(v_id2))
        report_content = report_content + report_lines
    return reduce(lambda a, b: a + b, report_content, '')

    
def memory_scan_batch(path, v_id1, v_id2):
    print "this is memory_scan_batch"
    # 随机获取虚拟机的列表
    import os
    # os.system("make")
    os.system("rmmod umu.ko")
    print '开始进行内存的生成'
    os.system("insmod umu.ko pid_from_user=%d log_file='%s/v_id1'" % (v_id1, path[0]))
    os.system("rmmod umu.ko")
    os.system("insmod umu.ko pid_from_user=%d log_file='%s/v_id2'" % (v_id2, path[0]))
    os.system("rmmod umu.ko")
    print '内存文件获取完成'
    # os.system("make clean")
    # os.system("python text.py")
    find_same()
    report_lines = mem_quchong(v_id1, v_id2)
    # 将虚拟内存和物理内存映射显示出来
    os.system("rm -rf v_id1")
    os.system("rm -rf v_id2")
    os.system("rm -rf v_final")
    return report_lines


def mem_quchong(v_id1, v_id2):
    import os
    import re
    report_lines = []

    ciku = open(r'v_final', 'r')
    xieci = open(r'v_result', 'a')

    sp = os.popen("ps %d" % (v_id1)).read()
    s1 = re.findall('guest=(.*?),', sp, re.S)
     
    sq = os.popen("ps %d" % (v_id2)).read()
    s2 = re.findall('guest=(.*?),', sq, re.S)

    head_line = "虚拟机进程号为:" + str(v_id1) + " " + "虚拟机名为:" + str(s1) + "\n" + \
                "虚拟机进程号为:" + str(v_id2) + " " + "虚拟机名为:" + str(s2) + \
                "的交叉页面地址如下：\n"
    xieci.writelines(head_line)
    report_lines.append(head_line)

    cikus = ciku.readlines()
    list2 = {}.fromkeys(cikus).keys()
    i = 0
    index = 0
    for line in list2:
        if not ('80000' in line):
            i += 1
            content_line = '0x'+line.replace('\n', '\t')
            xieci.writelines(content_line)
            if index <= 4:
                report_lines.append(content_line)
            if i == 6:
                i = 0
                xieci.write('\n')
                if index <= 4:
                    index += 1
                    report_lines.append('\n')
    # 写入分隔字符
    xieci.writelines("\n")
    xieci.close()
    return report_lines


if __name__ == '__main__':
    print memory_scan()








