#!/usr/bin/python
# -*- coding: utf-8 -*-
# Filename: common.py

# Author : Loonghu
# MailTo : caolonghu@sina.cn
# Created : 2015-5-5
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
       
    LOG_FILE = '/var/log/engine_ta/engine_ta.log'

    handler = logging.handlers.RotatingFileHandler(LOG_FILE,maxBytes = 1024*1024, backupCount = 5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    logger = logging.getLogger('my')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def test_get_logger():
    try:
        logger = get_logger()
        if(logger != None):
            logger.info('test logger info msg')
            logger.debug('test logger debug msg')
            logger.error("test logger error")
    except Exception,e:
        print str(e)
        
if __name__ == "__main__":
    print get_time()
    test_get_logger()
    print "Over"
