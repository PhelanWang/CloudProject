#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: disk_scan.py
__author__ = 'wz'


import os
import random

SCAN_SIZE = 52428800


def reduce_lines(contents, symbol):
    ret = ""
    j = 0
    a = contents.splitlines(True)
    for i, item in enumerate(a):
        if i >= 11:
            break
        if symbol in item:
            ret += item
            j += 1
            if j >= 4:
                break
    return ret

def get_vm_disk_size(vm_disk_path):
#     global IS_ERROR
#     if IS_ERROR==True or vm_disk_path=="":
#         return "0"
    try:
        file_info=os.popen('ls -l %s'%(vm_disk_path)).read().split(' ')
        return file_info[4]
    except:
        return "0"


def random_list(min, max, count):
    num_set = set()
    for i in range(count):
        num_set.add(random.randint(min, max))
    return num_set

def do_scan(disk_path, disk_size, symbol):
    scan_count = disk_size/SCAN_SIZE
    is_contain = False
    for i in random_list(random.randint(0, int(scan_count/2)), scan_count, 4):
        scan_content = os.popen('hexdump -C %s -n %s -s %s | grep "[_ .:]%s[_ .:]" -C 1 | more' \
                                % (disk_path, SCAN_SIZE, SCAN_SIZE*i, symbol)).read()
        if(len(scan_content) != 0):
            scan_content = reduce_lines(scan_content, symbol)
            if scan_content != '':
                result = "在扫描内容中发现相关内容:\n" + scan_content + "\n"
                is_contain = True
                break
    if not is_contain:
        result = " 在扫描内容中未发现"
#     if(is_contain==True and need_print==True):
#         result = result + "<br>" + scan_content +"<br>"
    return result

def symbol_scan(disk_path, disk_size):
    detail = "开始虚拟磁盘扫描:\n"
    detail += "虚拟磁盘大小:" + str(disk_size) + "\n"
#     windows_symbol_list=['microsoft','windows']
#     linux_symbol_list=['linux','jiffies']
    symbol_list = ['boot', 'root', 'environment', 'path', 'service', 'user', 'password']
    if disk_size == 0:
        return "磁盘错误, 无法获取磁盘空间信息!"
    try:
        is_contain = False
        for symbol in symbol_list:
            scan_result = do_scan(disk_path, disk_size, symbol)
            detail += "\n关键字:" + symbol + scan_result
            if not (scan_result == " 在扫描内容中未发现"):
                is_contain = True
                break
        detail += "\n虚拟磁盘扫描结束!"
        if is_contain:
            result = "发现关键字，虚拟磁盘未加密!"
        else:
            result = "未发现关键字，虚拟磁盘或许有加密!"
        ret = {"result": result, "detail": detail}
        return ret
    except:
        return "磁盘错误, 扫描出现未指定错误!"


if __name__ == "__main__":
    vm_disk_path = "/kvm/images/c8f5ff0c-52b5-490b-b9b4-d11b5e0e78e2/images/1aebe17c-f885-4f58-9a60-5307d700d88a/ec64733d-a88e-4325-8298-a09102946823"
    vm_disk_size=int(get_vm_disk_size(vm_disk_path))
    print symbol_scan(vm_disk_path,vm_disk_size)