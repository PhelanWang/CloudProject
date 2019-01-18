import xlrd,xlwt,os,re,commands
from datetime import date,datetime





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
  slist = out.split('-')
  return slist[0]

def libvirt_get_versions():
  slist={'libvirt':get_libvirt_version(),'redhat':get_redhat_release_version,'kernal':get_openstack_version()}
  return slist

if __name__ == '__main__':
    print 'ok'