#coding=utf-8
import os,sys
###########################################################################
path='/home/kvm/images/ee43aa37-1f5b-4664-8ca2-d447afabdf8b/images'
###########################################################################
def getVMDiskPath():
    if os.path.exists(path):
        return os.listdir(path)
    print u'磁盘目录不存在!'
    return []
    #pass

print getVMDiskPath()