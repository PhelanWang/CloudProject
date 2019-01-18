'''
Created on Jun 3, 2015

@author: zyc
'''
import logging.config
import os
import pexpect
import time
import ConfigParser


# nodeName = "nodeTest"
# vmTest = "test"



def vmMigrateScript(nodeName, vmTest):

    conf=ConfigParser.ConfigParser()
    conf.read("encryption/custom.conf")
    url=conf.get("Engine","URL").strip()
    userName=conf.get("Engine","userName").strip()
    password=conf.get("Engine","password").strip()
    domainName=conf.get("Engine","domainName").strip()

    time.sleep(3)
    child = pexpect.spawn('ovirt-shell -c -l "%s" -u "%s@%s" -I' % (url, userName, domainName))
    index = -1
    index = child.expect(["(?i)Password: ", pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        print "login, please input password"
        child.sendline("%s" % password)
        index = -1
        index = child.expect(["(?i)connected to oVirt manager", "(?i)Unauthorized", pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            print "login successfully"
            child.sendline("action vm %s migrate --host-name %s" % (vmTest, nodeName))
            index = -1
            index = child.expect(["(?i)status-state: complete", "(?i)status: 404", "(?i)status: 409", "(?i)does not exist", pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print "vm %s is migrating" % (vmTest)
            elif index == 1:
                print "vm %s migration failed, node %s does not exist" % (vmTest, nodeName)
            elif index == 2:
                print "vm %s migration failed, vm %s is not running" % (vmTest, vmTest)
            elif index == 3:
                print "vm %s migration failed, vm %s does not exist" % (vmTest, nodeName)
            else:
                print "vm %s migration failed" % (vmTest)
            child.sendline("exit")
            index = -1
            index = child.expect(["(?i)disconnected from oVirt manager", pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                print "logout successfully"
                child.close(force=True)
            else:
                print "disconnected error"
                child.close(force=True)
        else:
            print "password is wrong"
            child.close(force=True)
    else:
        print "login failed"
        child.close(force=True)

def isPathExist(path):
    logging.config.fileConfig("encryption/myLogging.conf")
    logger = logging.getLogger("ScratchPackLog")
    isExist = os.path.exists(path)
    if not isExist:
        try:
            os.mkdir(path)
            logger.info("create dir %s success!" % (path))
        except Exception, e:
            logger.error("mkdir %s error: " % (path) + str(e))
            return    
    else:
        logger.info("dir %s already exist!" % (path))
        
def isEnd(fp):
    filepointer = fp
    string = filepointer.read()
    if string == '':
        return True
    else:
        return False
    
def processLibvirtPack():
    logging.config.fileConfig("encryption/myLogging.conf")
    logger = logging.getLogger("ScratchPackLog")
    try:
        isPathExist("encryption/packlog")
        myFile1 = "encryption/packlog/originalpackLIBVIRT"
        myFile2 = 'encryption/packlog/filterpackLIBVIRT'
        os.popen('tshark -i any -R "tcp.port==16514 and data" -V -O data -a duration:30 > %s && grep  -i -E "memory|microsoft|kernel" %s > %s' % (myFile1, myFile1, myFile2))
        try:
            f = open(myFile2, "rb")
            f2 = open(myFile1, "rb")
        except Exception,e:
            print e
            return -1
        if not isEnd(f2):
            if isEnd(f):
                logger.info("scratch no packages that match the vm memory string")
                f.close()
                f2.close()
                return 1
            else:
                logger.info("scratch some packages that match the vm memory string")
                f.close()
                f2.close()
                return 2
        else:
            return 3
    except Exception, e:
        logger.error("processPack error: " + str(e))
        return -1

     
# thread.start_new_thread(vmMigrateScript, ())
# if processLibvirtPack():
#     print "the data is encrypted"
# else:
#     print "the data is unencrypted"

