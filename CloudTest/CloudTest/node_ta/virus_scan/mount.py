#! coding=utf-8
import logging
from subprocess import *
from commands import *
import time
import os
import threading
import string
import ctypes
logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


# 挂载器
class Mounter(object):

    def __init__(self, img_path, os_name):
        self.img_path = img_path
        self.os_name = os_name

    def killid(self):
        pid_str = " ps -ef |grep qemu-kvm |grep -v grep |grep kristen|awk '{print $2}'"
        print pid_str
        pidlist = os.popen(pid_str).read().strip().split('\n')
        print 'pidlist'
        print (pidlist)
        for pid in pidlist:
            if pid == '':
                pass
            else:
                strs = "kill -9 %s" % (pid)
                print strs
                os.system(strs)

    def check_available(self):
        rpt = ""
        self.killid()
        str_size = "qemu-img info %s | grep disk |cut -d ' ' -f 3  |grep K" % self.img_path
        print str_size
        size = os.popen(str_size).read().strip()
        if size == '':
            print "disk check ok"
            return True
        else:
            print "can not mount!"
            return False

    def mount(self):
        check_disk = self.check_available()
        if check_disk == False:
            return False
        else:
            print 'create thread start'
            t1 = startvm(self.img_path,name='kristen01')
            t2 = startvm(self.img_path,name='kristen02')
            t1.start()
            t2.start()
            print 'create thread end'
            return True

    def getReport(self):
        flag = self.mount()
        if not flag:
            return False
        elif flag:
            try:
                pid1 = os.popen("ps -ef |grep -v grep |grep qemu-kvm |grep kristen01|awk {'print $2'}").read().strip('\n')
                print 'pid1', pid1
                pid2 = os.popen("ps -ef |grep -v grep |grep qemu-kvm |grep kristen02|awk {'print $2'}").read().strip('\n')
                print 'pid2', pid2

                port1 = os.popen("netstat -ntpl |grep  "+pid1+" |grep qemu-kvm |awk '{print $4}' |cut -d ':' -f 4" ).read()
                port2 = os.popen("netstat -ntpl |grep  "+pid2+" |grep qemu-kvm |awk '{print $4}' |cut -d ':' -f 4" ).read()
                
                port1 = port1.strip('\n')
                port2 = port2.strip('\n')
                rst = "对磁盘镜像启动第一个虚拟机 vm1"
                if port1 != '':
                    rst += " 启动成功, 虚拟机 VNC 服务运行在端口 %s。 \n" % str(port1)
                else:
                    rst += ' 启动失败。\n'

                rst = rst + '对镜像启动第二个虚拟机 vm2'
                if port2 != '':
                    rst += " 启动成功, 虚拟机 VNC 服务运行在端口 %s 。\n" % str(port2)
                else:
                    rst += ' 启动失败。\n'
#                 rst = rst.strip(' ') +"start vm2 , VNC server running on %s" % str(port2)

                if (port1 == '' and port2 != '') or (port1 != '' and port2 == ''):
                    rst += '测试表明对于同一个磁盘，只能启动一个虚拟机，不能够多重挂载该虚拟机磁盘。'
                elif port1 != '' and port2 != '':
                    rst += '测试表明对于同一个磁盘，能够启动一个以上的虚拟机，能够多重挂载该虚拟机磁盘。'
                elif port1 == '' and port2 == '':
                    rst += '对指定镜像两个虚拟机都不能够挂载，请检查磁盘路径是否正确。\n' \
                           '都不能启动可能受云平台环境影响，可稍后再测试。'
                return rst
            except:
                print "throw exception on start vms "
                return False
            # print 'start vms success with disk listen on port %s'%str(5900)


class startvm(threading.Thread):
    def __init__(self,path,name):
        threading.Thread.__init__(self,name=name)
        self.path =path
        self.thread_stop=False

    def run(self):
        #while not self.thread_stop:
        print 'start vm'
        os.system("/usr/libexec/qemu-kvm -m 2048 -name %s %s" % (self.name, self.path))
        time.sleep(1)
        print 'Thread  start %s,Time %s \n' % (self.path,time.ctime())

    def stop(self):
        self.thread_stop = True

    def getpid(self):
        return ctypes.CDLL('libc.so.6').syscall(186)
'''
def test():
    thread1=startvm("tt1")
    thread2=startvm("tt2")
    thread3=startvm("tt3")
    thread1.start()
    thread2.start()
    thread3.start()
    print 'pakistan'
    time.sleep(20)
    thread1.stop()
    thread2.stop()
    thread3.stop()

if __name__ == "__main__":
    logging.debug("hello")
    pathdisk="/run/media/root/080be9a2-5944-4428-86b5-6f0e9da6269e/kvm/image/6cc1c44f-aa0a-4876-80b3-ab1a49896c47/images/5ef6324a-d688-4dee-847b-0b36cbc78c2a/d58e4ccf-dab5-44ef-a338-b41dfcc264bd"

    #空磁盘
    #pathdisk="/run/media/root/080be9a2-5944-4428-86b5-6f0e9da6269e/kvm/image/6cc1c44f-aa0a-4876-80b3-ab1a49896c47/images/4fd56f4c-1948-45b8-9692-df3c0f0986f9/0c39fd9c-78bd-4447-9aab-0db1cc8ffd65"
    mt = Mounter(pathdisk, 'test')

    #print 'thread id : ' ,ctypes.CDLL('libc.so.6').syscall(186)
    mt.getReport()

    '''
  