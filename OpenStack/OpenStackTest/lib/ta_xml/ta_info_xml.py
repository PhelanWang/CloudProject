#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: ta_info_xml.py

# Author : Loonghu
# MailTo : caolonghu@sina.cn
# Created : 2015-07-11
# Version: 1.0

from xml.etree import ElementTree
import xml.dom.minidom as minidom

from lib.node_ta.ta_common import *


#===============================================================================
# var:
# dm_path: dump-memory exec file's path
# gg_path: getGUID exec file's path
# tmp_dir: data tmp storage
#
# return:
#    smc_data: type list, {dm_path:"",gg_path:"",tmp_dir:""}
#    False: failed to get sec_mem configure
#===============================================================================
def load_sec_mem_conf():
    filename = "/etc/node_ta/sec_mem.xml"

    dm_path = ""
    gg_path = ""
    tmp_dir = ""
    libvmi_user = ""
    libvmi_password = ""
    
    smc_data = {} # security memory configure data

    content = ""
    try:
        content = open(filename).read()
    except Exception,e:
        logger.error("error get sec mem conf " + str(e))
        return False

    try:
        root = ElementTree.fromstring(content)
    
        lst_infos = root.getiterator("sec_mem")[0].getchildren()

        for item in lst_infos:
            tag = item.tag
            text = item.text.strip()
            #print tag,text
            if tag == 'dm_path':
                smc_data[tag] = text
            elif tag == 'gg_path':
                smc_data[tag] = text
            elif tag == 'tmp_dir':
                smc_data[tag] = text
            elif tag == 'libvmi_user':
                smc_data[tag] = text
            elif tag == 'libvmi_password':
                smc_data[tag] = text
            else:
                pass
    except Exception,e:
        logger.error("error get sec mem conf " + str(e))
        return False
    return smc_data

#smc_data = load_sec_mem_conf()
#if smc_data:
#    print smc_data
#else:
#    print "Error"


#def _test_load_sec_mem_conf():
    #print "test load sec mem conf .. "


if __name__ == "__main__":
#     _test_get_engine_api_conf()
    #_test_load_sec_mem_conf()
    print " Test Over"
