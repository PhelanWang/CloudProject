#! /usr/bin/python
#encoding=utf-8
#all info out!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#from sqlutils.sqlhelper import getConnection,closeConn
import sys
import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from scanflaw.type_tran import get_enterprise_virtualization_version
def getFlawInfoBySql(sql):
  con = sqlite3.connect('quick_flaw_scan/cloud.db')
  cur = con.cursor()
  versions = get_enterprise_virtualization_version()
  print 'versions:', versions
  #versions = {'redhat': '3.2','cisco': '3.3.1','ubuntu': 'none'}
  inum = cur.execute(sql)
  inlist=[]
  fitinlist = []
  while(1):
    row = cur.fetchone()
    if(row==None):
      break
    #row[[7]产品信息，row[8]版本信息，row[2]漏洞名称，row[4]漏洞信息
    pro = row[7]
    ver = row[8]
    #tes =  pro.find(",")
    #print tes
    if(pro.find(",")>=0):

        #多个产品,取出产品版本,多个产品时qemu版本未指定的情况未检测
        #s = "漏洞名称：%s \n" % row[2].replace('\n','')+ "漏洞信息：%s \n" % row[4].replace('\n','')
        #inlist.append(s)

        prol = pro.split(",")
        verl = ver.split("_")
        for i in range (len(prol)):
            for key in versions:
                if(prol[i]==key):
                    if(verl[i].find(versions.get(key))>=0):
                        sfit = {'bugName': "%s \n" % row[2].replace('\n', ''), 'bugInfo': "%s \n" % row[4].replace('\n', '')}
                        fitinlist.append(sfit)
    if(pro.find(",")<0):
        #单个产品 huozhe chanping yilan wei "null"
        #if(pro=="null"):
        #      s = "漏洞名称：%s \n" % row[2].replace('\n','')+ "漏洞信息：%s \n" % row[4].replace('\n','')
        #      inlist.append(s)
        #else:
        #      s = "漏洞名称：%s \n" % row[2].replace('\n','')+ "漏洞信息：%s \n" % row[4].replace('\n','')
        #      inlist.append(s)

        for key in versions:
                if(pro==key):
                    if(ver.find(versions.get(key))>=0):
                        sfit = {'bugName': "%s \n" % row[2].replace('\n', ''), 'bugInfo': "%s \n" % row[4].replace('\n', '')}
                        fitinlist.append(sfit)
        #if(pro=="qemu" and ver.find(versions.get('qemu'))>=0):
        #      s = "漏洞名称：%s \n" % row[2].replace('\n','')+ "漏洞信息：%s \n" % row[4].replace('\n','')
        #      inlist.append(s)
  cur.close()
  con.close()
 ##addtional operate()
  con = sqlite3.connect('quick_flaw_scan/cloud.db')

  cur = con.cursor()  
  inum = cur.execute(sql+" where version='产品及版本信息(CPE)暂不可用'")
  while(1):
    row = cur.fetchone()
    if(row==None):
        break
    sfit = {'bugName': "%s \n" % row[2].replace('\n', ''), 'bugInfo': "%s \n" % row[4].replace('\n', '')}
    fitinlist.append(sfit)
  cur.close()
  con.close()
  #con.clo###
  #return inlist
  if not fitinlist:
      return []
  return fitinlist

if __name__ == '__main__':
  reload(sys)
  sys.setdefaultencoding('utf-8')
  
  slist = getFlawInfoBySql("select * from VDSM_flaw_scan")
  for sfit in slist:
	print sfit
  #for sfit in slist:
   # print sfit