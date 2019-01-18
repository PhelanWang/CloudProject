#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: ta_xml.py

# Author : Loonghu
# MailTo : caolonghu@sina.cn
# Created : 2015-5-5
# Version: 1.0

from xml.etree import ElementTree
import xml.dom.minidom as minidom

def get_engine_api_conf():
    filename = "install/examples/info/info.xml"

    url = ""
    username = ""
    password = ""
    ca_file = ""

    eac_data = {} # engnine api conf data

    content = ""
    try:
        content = open(filename).read()
    except Exception,e:
        print str(e)
        print "Cannot open " + filename

    try:
        root = ElementTree.fromstring(content)
    
        lst_infos = root.getiterator("engine_api")[0].getchildren()

        for item in lst_infos:
            tag = item.tag
            text = item.text.strip()
            if tag == 'url':
                eac_data[tag] = text
            elif tag == 'username':
                eac_data[tag] = text
            elif tag == 'password':
                eac_data[tag] = text
            elif tag == 'ca_file':
                eac_data[tag] = text
            else:
                pass
    except Exception,e:
        print str(e)
        print "Cannot get info from xml of " + filename
    return eac_data

def get_ipscan():
    filename = "install/examples/info/info.xml"
    ipscan = ""
    
    content = ""
    try:
        content = open(filename).read()
    except Exception,e:
        print str(e)
        print "Cannot open " + filename

    try:
        root = ElementTree.fromstring(content)
    
        lst_infos = root.getiterator("subnets")[0].getchildren()

        for item in lst_infos:
            tag = item.tag
            text = item.text.strip()
            if tag == 'subnet':
                ipscan = text
            else:
                pass
    except Exception,e:
        print str(e)
        print "Cannot get info from xml of " + filename
        
    
    return ipscan
    
def _test_get_engine_api_conf():
    eac_data = get_engine_api_conf()
    if(eac_data == {}):
        print "[error] get info of engine conf data"
    else:
        print eac_data

def _test_get_ipscan():
    ipscan = get_ipscan()
    print ipscan
    
if __name__ == "__main__":
    _test_get_engine_api_conf()
    #_test_get_ipscan()
    print " Test Over"
