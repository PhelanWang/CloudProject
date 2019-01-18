# coding: utf8

__author__ = 'zyc'

# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)


# 格式修改完成
@agent.entry("testLDAP", version="1.0.1")
def my_testLDAP(subtask_id, args):
    from encryption.processLDAP import loginScript, processLDAPPack, stringLDAPMatch
    import ConfigParser

    conf = ConfigParser.ConfigParser()
    conf.read('encryption/custom.conf')
    userName = conf.get('Engine', 'userName').strip()
    userPassword = conf.get('Engine', 'password').strip()
    domainName = conf.get('Engine', 'domainName').strip()

    # thread.start_new_thread(loginScript,(userName, userPassword, domainName))
    sstri = processLDAPPack('localhost')
    fileName="encryption/packlog/filterpackLDAP"
    try:
        f = open(fileName, "r")
        readbuf = f.readlines()
        f.close()
    except Exception,e:
        # agent.post_report(subtask_id, 0, 0, 'done', 'scratch no package', json_data={"data":""})
        print e
    # sendbuf = pattern.sub("<br/>", readbuf)
    flag = stringLDAPMatch()
    if sstri != '':
        print reduce(lambda a, b: a+b, readbuf[:68], '')
        agent.post_report(subtask_id, 0, 1,
                          brief='done',
                          detail='云平台LDAP数据传输协议是加密的。',
                          json_data=reduce(lambda a, b: a+b, readbuf, '').replace('\n', '<br>'))
        print "the data is encrypted"
    elif flag == 2:
        agent.post_report(subtask_id, 0, 0,
                          brief='done',
                          detail='云平台LDAP数据传输协议是加密的。',
                          json_data=reduce(lambda a, b: a + b, readbuf, '').replace('\n', '<br>'))
        print "the data is unencrypted"


# 格式修改完成
@agent.entry("testSSH", version="1.0.1")
def my_testSSH(subtask_id, args):
    from encryption.processSSH import stringMatchSSH, procSSHPack, addHostScript

    array = ['encryption:aes128-ctr', 'Encrypted Packet:']
    if procSSHPack("localhost"):
        fileName = "encryption/packlog/filterpackSSH"
        try:
            f = open(fileName,"r")
            readbuf = f.readlines()
            f.close()
        except Exception,e:
            print e
        if stringMatchSSH(array):
            print reduce(lambda a, b: a+b, readbuf, '')
            agent.post_report(subtask_id, 0, 1,
                              brief='done',
                              detail='云平台SSH数据传输协议是加密的。',
                              json_data=reduce(lambda a, b: a+b, readbuf, ''))
            print "the data is encrypted"
        else:
            agent.post_report(subtask_id, 0, 0,
                              brief='done',
                              detail='云平台SSH数据传输协议是未加密的。',
                              json_data=reduce(lambda a, b: a+b, readbuf, ''))
            print "the data is unencrypted"


# 格式修改完成
@agent.entry("erase_scan", version="1.0.1")
def my_erase_scan(subtask_id, args):
    from sec_storage.disk_erase_detect import get_total_save, do_erase_scan
    import os

    print 'startup erase_scan'
    args = {'path': os.getcwd()+'/sec_storage/test-disk'}
    print args['path']
    disk_path = args['path']

    result = get_total_save(disk_path)
    if result == "ERROR":
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail='进行磁盘扫描失败。\n'.replace('\n', '</br>'),
                          json_data="进行指定磁盘扫描失败，请检查给定路径是否正确。\n".replace('\n', '</br>'))
        return
    os.system('cp ' + disk_path + ' ' + disk_path + '1')
    os.system('rm ' + disk_path)
    report = do_erase_scan()
    os.system('mv ' + disk_path + '1' + ' ' + disk_path)
    if not report:
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail='进行磁盘扫描失败。\n'.replace('\n', '</br>'),
                          json_data="进行指定磁盘扫描失败，请检查给定路径是否正确。\n".replace('\n', '</br>'))
    else:
        print 'report', report['result'], 'detail', report['detail']
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail=report['detail'].replace('\n', '</br>'),
                          json_data=report['result'].replace('\n', '</br>'))


# Execute this while run this agent file directly
if not is_load_external():
    args = {}
    # args["id"] = 'localhost'
    # my_testLDAP(0, args)
    # my_testSSH(0, args)
    # Run agent
    # args['path'] = '/root/PycharmProjects/test/1fe0032b-aabd-4315-8390-6bbac5844ea5'
    # args['name'] = '1fe0032b-aabd-4315-8390-6bbac5844ea5'

    # my_disk_scan(0, args)
    # my_erase_scan(0, args)
    agent.run()

