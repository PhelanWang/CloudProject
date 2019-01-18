# coding: utf-8

import os


# 比较两个版本的大小，版本格式x.xx或x.x
def version_comapre(v1, v2):
    if not '.' in v1:
        return False
    v1 = v1.split('.')
    v2 = v2.split('.')
    if int(v1[0]) > int(v2[0]):
        return True
    elif int(v1[0]) == int(v2[0]):
        if int(v1[1]) >= int(v2[1]):
            return True
    return False

# 将虚拟磁盘挂在到 /mnt目录下
def mount_disk(args):
    import time
    mod_path = os.getcwd() + '/access_detection/nbd.ko'
    os.system('insmod ' + mod_path + ' max_part=16')
    os.system('qemu-nbd -c /dev/nbd0 ' + args['path'])
    time.sleep(3)
    os.system('mount /dev/nbd0p1 /mnt')


def umount_disk():
    os.system('umount /mnt')
    os.system('qemu-nbd --disconnect /dev/nbd0')
    os.system('rmmod nbd.ko')


# 使用linux命令虚拟机磁盘，然后返回根目录下的文件的访问控制权限
def list_access_controll(args):
    mount_disk(args)
    result = ''.join(os.popen("ls -lh /mnt | awk '{print $1,$3,$4,$9}'").readlines()[1:])
    umount_disk()
    return result


# 获取虚拟机的版本信息
def get_vm_infor(args):
    mount_disk(args)
    result = '虚拟机系统内核名称: '
    kernal_name = os.popen('/mnt/bin/uname -s').read()
    result += kernal_name
    result += '虚拟机主机名称: '
    result += os.popen('/mnt/bin/uname -n').read()
    result += '虚拟机内核发行号: '
    version = os.popen('/mnt/bin/uname -r').read()
    result += version
    result += '虚拟机架构: '
    result += os.popen('/mnt/bin/uname -i').read()
    result += '虚拟机操作系统版本: '
    result += os.popen('cat /mnt/etc/issue').read()
    umount_disk()
    return result, version.split('-')[0]
