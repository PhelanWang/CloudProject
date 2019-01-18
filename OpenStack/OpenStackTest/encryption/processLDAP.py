# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Jul 13 2018, 13:06:57) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
# Embedded file name: /root/git/ovirt/engine_ta/encryption/processLDAP.py
# Compiled at: 2016-09-27 20:01:42
"""
Created on Jun 3, 2015

@author: zyc
"""
import commands, logging.config, os, re, time, ConfigParser, pexpect

def loginScript(userName, userPassword, domainName):
    conf = ConfigParser.ConfigParser()
    conf.read('encryption/custom.conf')
    url = conf.get('Engine', 'URL').strip()
    time.sleep(3)
    conf = ConfigParser.ConfigParser()
    conf.read('encryption/custom.conf')
    url = conf.get('Engine', 'URL').strip()
    print 'ovirt-shell -c -l "%s" -u "%s@%s" -I' % (url, userName, domainName)
    child = pexpect.spawn('ovirt-shell -c -l "%s" -u "%s@%s" -I' % (url, userName, domainName))
    index = child.expect(['(?i)Password: ', pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print 'login, please input password'
        child.sendline('%s' % userPassword)
        index = child.expect(['(?i)connected to oVirt manager', '(?i)Unauthorized', pexpect.EOF, pexpect.TIMEOUT])
        index = 0
        if index == 0:
            print 'login successfully'
            child.sendline('exit')
            index = child.expect(['(?i)disconnected from oVirt manager', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print 'logout successfully'
                child.close(force=True)
            else:
                print 'disconnected error'
                child.close(force=True)
        else:
            print 'password is wrong'
            child.close(force=True)
    else:
        print 'login failed'
        child.close(force=True)


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


def isEnd(fp):
    filepointer = fp
    string = filepointer.read()
    if string == '':
        return True
    return False


def processLDAPPack(addr):
    logging.config.fileConfig('encryption/myLogging.conf')
    logger = logging.getLogger('ScratchPackLog')
    isPathExist('encryption/packlog')
    myFile = 'encryption/packlog/originalpackLDAP'
    myFile2 = 'encryption/packlog/filterpackLDAP'

    ip = 'ip.src == %s' % addr
    os.popen('tshark -i any -R "ldap and (%s)" -a duration:30 -V > %s1' % (ip, myFile))
    os.system('rm '+myFile+'1')
    # return os.popen('cat encryption/packlog/originalpackLDAP').read()
    f = open(myFile, 'rt')
    if isEnd(f):
        logger.info('scratch no packages')
        f.close()
        return
    f.seek(0, 0)
    f2 = open(myFile2, 'wr+')
    pattern1 = re.compile('\\s*Lightweight\\s*Directory\\s*Access\\s*Protocol\\s*')
    pattern2 = re.compile('\\s*Frame\\s*\\d+')
    while True:
        string = f.readline()
        if string == '':
            if isEnd(f):
                break
        if pattern1.match(string):
            f2.writelines(string)
            while True:
                string = f.readline()
                if pattern2.match(string):
                    break
                if string == '' or string == '\n':
                    break
                f2.writelines(string)

            f2.writelines('\n')

    f2.close()
    f.close()
    logger.info('processPackLDAP successful!')


def stringLDAPMatch(myFile='encryption/packlog/filterpackLDAP'):
    logging.config.fileConfig('encryption/myLogging.conf')
    logger = logging.getLogger('ScratchPackLog')
    try:
        pattern1 = re.compile('\\s*Encryption\\s*type:\\s+(.+)')
        pattern2 = re.compile('\\s*GSS-API\\s*Encrypted\\s*payload\\s*')
        try:
            f = open(myFile, 'rb')
        except Exception as e:
            print e
            return -1

        if isEnd(f):
            logger.info('scratch no packages')
            f.close()
            return -1
        f.seek(0, 0)
        while True:
            readbuff = ''
            readbuff = f.read()
            if readbuff == '':
                break
            encList = pattern1.findall(readbuff)
            print 'the encryption type: ' + encList[0]
            if pattern1.search(readbuff) or pattern2.search(readbuff):
                logger.info('string match successful!')
                return 1

        logger.info('string match failed!')
        f.close()
        return 2
    except Exception as e:
        logger.error('stringMatchLDAP error: ' + str(e))