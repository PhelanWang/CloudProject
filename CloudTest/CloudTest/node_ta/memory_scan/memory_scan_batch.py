#!/usr/bin/python
#coding=utf-8
import os;
import sys;
import re;
import random;    
from memory_scan.memory_quchong import mem_quchong;
def mem(path,v_id1,v_id2):
    print 'hello'
    #随机获取虚拟机的列表
    str = os.popen("pidof 'qemu-kvm'").read()
    a = str.split("\n")
    cc=a[0]
    strq=cc.split(" ")
    slice=random.sample(strq, 2)
    #v_id1=int(slice[0])
    #v_id2=int(slice[1])
    #
    print os.getcwd()
    #os.system("rm -rf v_result")
    os.system("make");
    os.system("rmmod umu.ko");
    os.system("rmmod umu.ko");
    print '开始进行内存的生成'
    os.system("insmod umu.ko pid_from_user=%d log_file='%s/v_id1'"%(v_id1,path[0]))
    os.system("rmmod umu.ko");
    os.system("insmod umu.ko pid_from_user=%d log_file='%s/v_id2'"%(v_id2,path[0]))
    print '内存文件获取完成'    
        #已经获取所需要的文本，将所需模块卸载
    os.system("make clean");
    os.system("rmmod umu.ko");
    os.system("python text.py");
    #os.system("python rmthesametxt.py");
    mem_quchong(v_id1,v_id2)
    print "yes"   
    #将虚拟内存和物理内存映射显示出来
    #os.chdir("%s/vm_map"%(path[0]))
    #print os.getcwd();
    #os.system("make");
    #os.system("rmmod vmem.ko ");
    #os.system("insmod vmem.ko pid_from_user=%d log_file='%s/vm_map/vm_1'"%(v_id1,path[0]))
    #print path[0]
    #print v_id1
    #os.system("rmmod vmem.ko ");
    #os.system("insmod vmem.ko pid_from_user=%d log_file='%s/vm_map/vm_2'"%(v_id2,path[0]))
    #print v_id2
    #os.system("make clean")
    #os.system("rmmod vmem.ko");
    #os.chdir("%s"%(path[0]))
    os.system("rm -rf v_id1")
    os.system("rm -rf v_id2")
    os.system("rm -rf v_final")
