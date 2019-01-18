#coding=utf-8
import os,re,commands
from datetime import date,datetime

#get kvm version
def get_ubuntu_version():
  (status,out) = commands.getstatusoutput('cat /etc/issue')
  if(out.find('Ubuntu')>=0):
      slist = out.split(' ')
      num =slist.index('Ubuntu')
      return slist[num+1]
  else :
    return 'none'

def get_qemu_version():
  (status,out)=commands.getstatusoutput('qemu-img --help | grep version')
  slist = out.replace(',','').split(' ')
  num = slist.index('version')
  return slist[num+1]


def get_kernal_version():
  (status,out)=commands.getstatusoutput('uname -r')
  slist = out.split('-')
  return slist[0]

def get_versions():
  slist={'qemu':get_qemu_version(),'ubuntu':get_ubuntu_version(),'kernal':get_kernal_version()}
  return slist

def get_flaw_info():
  flist = tran_type('cve.xlsx')
  version = get_qemu_version()
  restr = ''
  version = version.replace('.','\.')
  pattern = re.compile(version)
  for e in flist:
   #print type(e)
   match = pattern.search(e)
   if match:
    print e


#libvirt-getVersion
def get_redhat_release_version():
  (status,out) = commands.getstatusoutput('cat /etc/redhat-release')
  if(out.find('enterprise_linux:6')>=0):
      slist = 'enterprise_linux:6'
      return slist;
  elif(out.__len__()!=0):
      slist = out.split(' ')
      num =slist.index('release')
      return slist[num+1]
  else:
      return 'none'

def get_libvirt_version():
  (status,out)=commands.getstatusoutput('rpm -qa|grep libvirt')
  slist = out.replace(',','').split('-')
  num = slist.index('client')
  return slist[num+1]
  
'''#新版本的 OpenStack Nova 提供了简单的管理员接口，不再需要通过 API 调用了：
# nova-manage version list
2011.3-dev (2011.3-workspace:tarmac-20110428165803-elcz2wp2syfzvxm8)'''

def get_openstack_version():
  (status,out)=commands.getstatusoutput('nova-manage version list')
  if(out.find('未找到命令')):
      return 'none'
  else:
      slist = out.split('-')
      return slist[0]

def libvirt_get_versions():
  slist={'libvirt':get_libvirt_version(),'redhat':get_redhat_release_version(),'openstack':get_openstack_version()}
  return slist

#Ovirt_scan
def get_rhevm_version():
  (status,out)=commands.getstatusoutput('rpm -qa|grep rhevm')
  if(out.find('未找到命令')):
      return 'none'
  if(out.find('3.0')):
      slist = '3.0'
  elif(out.find('3.1')):
      slist = '3.1'
  elif(out.find('3.2')):
      slist='3.2'
  elif(out.find('3.3')):
      slist ='3.3'
  else:
      slist='none'
  return slist


def get_rbovirt_version():
  (status,out)=commands.getstatusoutput('rpm -qa|grep rbovirt')
  if(out.find('未找到命令')):
      return 'none'
  slist0 ='0.0.19,0.0.20,0.0.21,0.0.8,0.0.9,0.0.10,0.0.6,0.0.11,0.0.7,0.0.12,0.0.4,0.0.22,0.0.13,0.0.5,0.0.23,0.0.14,0.0.17,0.0.18,0.0.15,0.0.16,0.0.3,0.0.2,0.0.1'
  slist = slist0.replace(',','').split(',')
  slist.index('0.0.19')
  for i in slist:
      if out.find(slist[i]):
          return slist[i]
  return 'none'

def ovirt_version():
  (status,out)=commands.getstatusoutput('rpm -qa|grep ovirt')
  if(out.find('未找到命令')):
      return 'none'
  if(out.find('ovirt-engine')):
        if(out.find('3.1.0.5')):
            return '3.1.0.5'
  elif(out.find('ovirt-engine-cli')):
      if(out.find('3.1.0.5')):
          return '3.1.0.5'
  elif(out.find('ovirt')):
      if(out.find('3.1')):
          return '3.1'
  else:
      return 'none'

def ovirt_get_versions():
  slist={'ovirt':ovirt_version(),'rbovirt':get_rbovirt_version(),'rhevm-reports':get_rhevm_version()}
  return slist


#get VDSM version
def get_enterprise_virtualization_version():
    line = os.popen('rpm -qa | grep ovirt-engine-backend').read()
    try:
        version = re.findall(r'([0-9].[0-9])', line)[0]
    except:
        version = '4.2'
    return version

def VDSM_get_versions():
  slist={'enterprise_virtualization':get_enterprise_virtualization_version()}
  return slist


if __name__ == '__main__':
  d= get_versions()
  for key in d:
      print key +" = " +d.get(key)
