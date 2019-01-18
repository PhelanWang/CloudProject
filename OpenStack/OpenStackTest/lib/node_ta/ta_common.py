#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: common.py

# Author : Loonghu
# MailTo : caolonghu@sina.cn
# Created : 2015-07-11
# Version: 1.0

import time
import sys
import re

import logging
import logging.handlers

def get_time():
    now = time.strftime("%H:%H:%S")
    date = time.strftime("%Y-%M-%d")
    return date + " " + now

def get_logger():
       
    import os
       
    LOG_FILE = '/var/log/node_ta/node_ta.log'

    if not os.path.exists(LOG_FILE):
        os.mkdir('/var/log/node_ta/')
       
        
    handler = logging.handlers.RotatingFileHandler(LOG_FILE,maxBytes = 1024*1024, backupCount = 5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    logger = logging.getLogger('node_ta')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

logger = get_logger()

def test_get_logger():
    try:
        if(logger != None):
            logger.info('test logger info msg')
            logger.debug('test logger debug msg')
            logger.error("test logger error")
    except Exception,e:
        print str(e)
     
def write_to_file(filename,data):
    file_object = None;
    flag = True
    try:
        file_object = open(filename,"w")
        file_object.write(data)
    except Exception,e:
        logger.error('Error write file ' + str(e))
        flag =  False
    finally:
        try:
            file_object.close()
        except Exception,e:
            logger.error('Error write file ' + str(e))
            flag = False
    return flag

#print write_to_file("/tmp/good/write","one\ntwo\nthree\n")

if __name__ == "__main__":
    print get_time()
    test_get_logger()
    print "Over"
