# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Jul 13 2018, 13:06:57) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
# Embedded file name: /root/git/ovirt/engine_ta/encryption/processSSH.py
# Compiled at: 2016-05-23 10:39:39
"""
Created on Apr 30, 2015

@author: zyc
"""
import logging.config, os, re, thread, time, ConfigParser, pexpect

def isEnd(fp):
    filepointer = fp
    string = filepointer.read()
    if string == '':
        filepointer = None
        return True
    filepointer = None
    return False
    return


def addHostScript(nodeName, nodeAddr, rootPassword):
    conf = ConfigParser.ConfigParser()
    conf.read('encryption/custom.conf')
    url = conf.get('Engine', 'URL').strip()
    userName = conf.get('Engine', 'userName').strip()
    password = conf.get('Engine', 'password').strip()
    domainName = conf.get('Engine', 'domainName').strip()
    time.sleep(3)
    child = pexpect.spawn('ovirt-shell -c -l "%s" -u "%s@%s" -I' % (url, userName, domainName))
    index = -1
    index = child.expect(['(?i)Password: ', pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print 'login, please input password'
        child.sendline('%s' % password)
        index = -1
        index = child.expect(['(?i)connected to oVirt manager', '(?i)Unauthorized', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print 'login successfully'
            child.sendline('add host --name %s --address %s --root_password "%s"' % (nodeName, nodeAddr, rootPassword))
            index = -1
            index = child.expect(['(?i)certificate-organization', '(?i)status: 400', '(?i)status: 409', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print 'the node is installing'
            else:
                if index == 1:
                    print 'The Host name is already in use, please choose a unique name and try again'
                else:
                    if index == 2:
                        print 'SSH authentication failed, verify authentication parameters are correct (Username/Password, public-key etc.)'
                    else:
                        print 'add node %s failed !!' % nodeName
            child.sendline('q')
            child.sendline('exit')
            index = -1
            index = child.expect(['(?i)disconnected from oVirt manager', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print 'logout successfully'
                child.close(force=True)
            else:
                print 'disconnected error'
                child.close(force=True)
        else:
            print 'password is wrong'
    else:
        print 'login failed!!'


def isPathExist(path):
    logging.config.fileConfig('encryption/myLogging.conf')
    logger = logging.getLogger('ScratchPackLog')
    isExist = os.path.exists(path)
    if not isExist:
        try:
            os.mkdir(path)
            logger.info('create dir %s success!' % path)
        except Exception as e:
            logger.error('mkdir %s error: ' % path + str(e))
            return

    else:
        logger.info('dir %s already exist!' % path)


def procSSHPack(addr):
    logging.config.fileConfig('encryption/myLogging.conf')
    logger = logging.getLogger('ScratchPackLog')
    try:
        isPathExist('encryption/packlog')
        myFile = 'encryption/packlog/originalpackSSH'
        myFile2 = 'encryption/packlog/filterpackSSH'
        ip = 'ip.addr == %s' % addr
        os.popen('tshark -i any -R "(tcp.port==22 and (ssh or data)) and (%s)" -a duration:120 -V > %s1' % (ip, myFile))
        os.system('rm '+myFile+'1')
        try:
            f = open(myFile, 'rt')
        except Exception as e:
            print e

        if isEnd(f):
            logger.info('scratch no packages')
            f.close()
            return False
        f.seek(0, 0)
        f2 = open(myFile2, 'wr+')
        pattern1 = re.compile('SSH\\s*Protocol\\s*')
        while True:
            string = f.readline()
            if string == '':
                if isEnd(f):
                    break
            if pattern1.match(string):
                f2.writelines(string)
                while True:
                    string = f.readline()
                    if string == '' or string == '\n':
                        break
                    f2.writelines(string)

        f2.close()
        f.close()
        logger.info('processPackSSH successful!')
        return True
    except Exception as e:
        logger.error('processPackSSH error: ' + str(e))


def stringMatchSSH(matchArray, myFile='encryption/packlog/filterpackSSH'):
    logging.config.fileConfig('encryption/myLogging.conf')
    logger = logging.getLogger('ScratchPackLog')
    try:
        string = ''
        for s in matchArray:
            string += '\\s*.*%s.*\\s*|' % str(s)

        string = string[:-1]
        pattern = re.compile(string)
        f = open(myFile, 'rb')
        if isEnd(f):
            logger.info('scratch no packages')
            f.close()
            exit()
        f.seek(0, 0)
        while True:
            readbuff = ''
            readbuff = f.read()
            if readbuff == '':
                break
            if pattern.search(readbuff):
                logger.info('string match successful!')
                return True

        logger.info('string match failed!')
        f.close()
        return False
    except Exception as e:
        logger.error('stringMatchSSH error: ' + str(e))