# -*- coding:utf-8 -*-
#import logging
#from subprocess import *
#from commands import *
import time

import  os
#import sys
import re
#import random
import commands


mpath = ''
ndebug = True
# default bin  path  is '/usr/libexec' ,  bin name can set
# default module path is /usr/lib/..
class VnicTest(object):
    qemu_kvm = ''
    ttype = ''
    def __init__(self,binname,ttype):
        self.qemu_kvm = binname
        self.ttype = ttype

    #only check if vms run
    # 使用vhost_net.ko旁路出网络数据
    # 加载vhost_net.ko模块要先关闭所有虚拟机，即关闭所有的qemu-kvm进程
    # 测试之前关闭虚拟机，点击测试之后再启动虚拟机
    # 该方法检测是否有qemu-kvm进程在执行
    def is_ready(self):
        pids = os.popen("pidof " + self.qemu_kvm).read().strip('\n').strip(' ')
        print pids
        if pids == '':
            return 'ok'
        else:
            return 'false'

    #if vms stop ,
    #   delete log begore test and
    #   begin replace bins and modules
    def begin(self):
        ready = self.is_ready()
        print "ready = " + ready
        # 删除vhost_net.log文件，卸载vhost_net模块，替换vhost_net.ko.xz文件
        if ready == "ok":
            # vhost_pck.log保存测试时旁路出的网络数据，加载模块时先删除该文件
            is_file = os.popen("ls /home/qemu/ | grep 'vhost_net.log'").read().strip("\n").strip(" ")
            if is_file == 'vhost_net.log':
                print "rm this file"
                os.system("rm -f /home/qemu/vhost_net.log")
            if ndebug:
                print('start replace. . .')
                self.replace()
            os.system("rmmod vhost_net")

            print("Please start vm. . .")
            print time.time()
            for i in range(5):
                print(i)
                time.sleep(60)
            print time.time()
            return True
        else:
            print "Stop all vms on this node!"
            return False

    #if install replace bins and modules don need this function
    # replace qemu-kvm or vhost_net.ko

    # 将系统文件夹下的 vhost_net.ko.xz 备份为 vhost_net.ko.xz.back
    # 将vnic文件夹下的 vhost_net.ko.xz 复制到系统文件夹下
    def replace(self):
        if self.ttype == 'vhost':
            # 获取系统的 vhost_net.ko.xz 的文件所在路径
            path = self.getpath()
            current_path = os.getcwd()
            current_path += '/vnic'
            os.system('mv ' + path + '/vhost_net.ko.xz ' + path + '/vhost_net.ko.xz.back')
            os.system('cp ' + current_path + '/vhost_net.ko.xz ' + path + '/vhost_net.ko.xz')

        if self.ttype == 'virtio':
            os.system('mv /usr/libexec/'+self.qemu_kvm+' /usr/libexec'+self.qemu_kvm+'.bk')
            os.system('cp ./qemu-kvm /usr/libexec/'+self.qemu_kvm+'')
            # cp default overwrite

    # This function need  all vms on this node had stopped ,
    # restore  the previous version
    # 将系统的 vhost_net.ko.xz 还原，将replace中备份的 vhost_net.ko.xz.back 还原为vhost_net.ko
    def disreplace(self):
        flag = self.is_ready()
        while(flag != 'ok'):
            self.shutdown()
            flag = self.is_ready()
        if flag == 'ok':
            if self.ttype == 'vhost':
                path = self.getpath()
                os.system('mv ' + path + '/vhost_net.ko.xz.back ' + path + '/vhost_net.ko.xz')

            if self.ttype == 'virtio':
                os.system('rm -f /usr/libexec/'+self.qemu_kvm+'')
                os.system('mv /usr/libexec/'+self.qemu_kvm+'.bk  /usr/libexec'+self.qemu_kvm+'')
                #os.system('cp ./qemu-kvm /usr/libexec/'+self.qemu_kvm+'')
        else:
            print "Stop all vms on this node !"

    def deal_hexdump(self):
        is_file = os.popen("ls /home/qemu/ | grep 'vhost_net.log'").read().strip("\n").strip(" ");
        if is_file == 'vhost_net.log':
            # os.system('text2pcap /home/qemu/vhost_net.log  /home/qemu/vhost_netlog')
            # out = commands.getstatusoutput("tshark -a duration:120 -Y 'http contains \"text/html\" and http contains \"HTTP/1.1 200 OK\"' -r /home/qemu/vhost_netlog  -V")
            # str = out[1]
            # smpout = commands.getstatusoutput("tshark -a duration:120 -Y 'http contains \"text/html\" ' -r /home/qemu/vhost_netlog ")
            # str2 = smpout[1]

            # htmlstr = re.findall(r'<html>.+?</html>', str, re.S)

            file = open('/home/qemu/vhost_net.log', 'r')
            str = file.read()
            # 获取所有请求头
            htmlstr = re.findall(r'GET.+?\r\n\r\n', str, re.S)
            if len(htmlstr) >= 1:
                report = {
                    "detail": '旁路网络数据成功，列出部分网络的请求头:\n',
                    "result": reduce(lambda a, b: a + b, htmlstr[:min(4, len(htmlstr))], '')
                }
            else:
                report = {
                    "detail": '旁路数据成功，但是未能查找到网络通信数据，请检测虚拟机是否能够访问网络。\n并在测试过程中，使用虚拟机访问网络，获取网页数据。',
                    "result": '请检查网络设置，正确访问网络并运行虚拟机!\n'
                }
        else:
            report = {
                "detail": '未能旁路网卡数据，请按步骤运行该测试功能，检查网络是否能够访问!\n并在测试过程中，使用虚拟机访问网络，获取网页数据。\n',
                "result": '请检查网络设置，正确访问网络并运行虚拟机!\n'
            }
        os.system('rm /home/qemu/vhost_net.log')
        return report

    # shutdown 会关闭所有的 qemu-kvm 虚拟机进程
    def shutdown(self):
         flag = self.is_ready()
         while flag != 'ok':
             pids = os.popen("pidof " + self.qemu_kvm + "").read().strip('\n').strip(' ').split(' ')
             for pid in pids:
                 os.system("kill -9 " + pid)
             flag = self.is_ready()
    # return report and disreplace
    def stop(self):
        self.shutdown()
        # 由于 shutdown 会关闭所有的虚拟机进程，所以模块以一定可以卸载模块
        os.system("rmmod vhost_net")
        if ndebug:
            # 还原文件
            self.disreplace()
        return self.deal_hexdump()
        #self.getreport()

    # return  report
    def getreport(self):
        pass

    # 获取系统加载vhost_net.ko.xz的路径
    # 系统加载vhost_net.ko模块在该文件夹下查找
    def getpath(self):
         #replace_reg = re.compile(r'vhost_net.ko$')
         #pwd = os.popen("find /lib/modules -name 'vhost_net\.ko' |grep $(uname -r)").read().strip('\n')
         #if(pwd==''):
         #    pwd = os.popen("find /usr/lib/modules -name 'vhost_net\.ko' |grep $(uname -r)").read().strip('\n')
         #path =  replace_reg.sub('',pwd)
         #print path +'path'
        return '/usr/lib/modules/$(uname -r)/kernel/drivers/vhost'


if __name__ == "__main__":
    vc = VnicTest('qemu-kvm', 'vhost')
    # vc.begin()
    # vc.stop()
    report = vc.deal_hexdump()
    # print report['brief']
    # print report['detail']