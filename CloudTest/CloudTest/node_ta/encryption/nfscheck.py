# coding: utf8
import os
import threading
import time
import pexpect as autologin
from nfsclient import sendmessage

class autoscript(object):
    def __init__(self):
        pass
    def ssh_cmd(self, password, cmd):
        ssh = autologin.spawn(cmd)
        try:
            i = ssh.expect([autologin.TIMEOUT, 'continue connecting (yes/no)?', 'password: '])
            if i==0:
                return None
            elif i==1:
                ssh.sendline("yes")
            ssh.sendline(password)

        except autologin.EOF:
            ssh.close()
        return ssh
    def combine_cmd(self, user, ip, command=''):
        cmdstr = "ssh %s@%s %s"%(user, ip, command)
        return cmdstr

class testnfs(object):
    def __init__(self, nfsip):
        self.nfsip = nfsip
        # self.nfsuser = nfsuser
        # self.nfspasswd = nfspasswd

    def edit_in_vm(self, user, ip, passwd, filename, test_text):
        test_text += "\n%s" % time.asctime()
        cmd_operate = '/bin/bash -c "cat > %s"' % filename
        ssh_login = autoscript()
        cmd = ssh_login.combine_cmd(user,ip,command=cmd_operate)

        ssh_session = ssh_login.ssh_cmd(passwd,cmd)
        ssh_session.sendline(test_text)
        ssh_session.sendcontrol('d')
        ssh_session.close()

    def edits_by_agent(self, filename, test_text):
        action = "test"
        test_text += "\n%s" % time.asctime()
        msg = "%s#%s#%s" % (action,filename,test_text)
        status = sendmessage(msg)
        return status

    def kill_tcpdump(self,passwd,choice):
        import os
        print 'kill: ', os.getcwd()
        os.system("bash encryption/dumpscript.sh %s %s" %(passwd,choice))
#         os.system("bash encryption/killScript.sh")
    def getdata(self,passwd):
        os.system("bash encryption/dumpscript.sh %s" % passwd)
#         os.system("bash encryption/getDataScript.sh")

class analysis(object):
    def __init__(self):
        pass
    def str_search(self,fileopen,search_for=None):
        result_list = []
        if search_for==None:
            return result_list
        else:
            for line in fileopen:
                if line.find(search_for)!=-1:
                    line = line.strip('\n')
                    result_list.append(line)
            fileopen.seek(0)
        return result_list

    def analsisdata(self,filename):
        fp = open("nfscap")
        result = False
        count = 0
        proof = ""
        try:
            for it in fp:
                if it.find('testnfs')!=-1:
                    break
            for y in range(20):
                proof+= fp.readline()
        except Exception,e:
            pass
        finally:
            fp.close()
        return [result,proof]

def entryfunction(nfsip, filename):
    nfspasswd = "123321" #if the script run as user, packets grab will need this
    proof = ""
    count = 0
    result = True
    mytest = testnfs(nfsip)
    myayalysis = analysis()
    dumpthread = threading.Thread(target=mytest.kill_tcpdump, args=(nfspasswd, 1))
#     dumpthread = threading.Thread(target=mytest.getdata, args=(nfspasswd))
    dumpthread.start()
    for x in range(5):
        time.sleep(2) 
        # edit_in_vm，是否要改成这个
        status = mytest.edits_by_agent('%s%s' % (filename, x),'This is a test in vms!')
        print status
    dumpthread.join()
    import os
    print os.getcwd()
    fp = open(os.getcwd() + '/encryption/nfscap')
#     fp = open('nfscap')
    for it in fp:
        if it.find(filename)!=-1:
            result = False
            fp.seek(count)
            break
        count +=len(it)
    for y in range(10):
        proof+= fp.readline()
    return [result,proof]




