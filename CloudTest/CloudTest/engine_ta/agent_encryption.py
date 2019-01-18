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
    from encryption.processLDAP import loginScript,processLDAPPack,stringLDAPMatch
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
    detail = 'LDAP是轻量目录访问协议，英文全称是Lightweight Directory Access Protocol\n' \
             '在云平台使用LDAP服务进行通信时，抓取通信数据' \
             '从数据中解析出了Lightweight Directory Access Protocol相关内容' \
             '并且使用GSS-API Generic Security Service Application Program Interface保证通信加密\n'
    if sstri != '':
        print reduce(lambda a, b: a+b, readbuf[:68], '')
        agent.post_report(subtask_id, 0, 1,
                          brief='done',
                          detail=(detail+'云平台LDAP数据传输协议是加密的。').replace('\n', '<br>'),
                          json_data=reduce(lambda a, b: a+b, readbuf, '').replace('\n', '<br>'))
        print "the data is encrypted"
    elif flag == 2:
        agent.post_report(subtask_id, 0, 0,
                          brief='done',
                          detail=(detail+'云平台LDAP数据传输协议是加密的。').replace('\n', '<br>'),
                          json_data=reduce(lambda a, b: a + b, readbuf, '').replace('\n', '<br>'))
        print "the data is unencrypted"


# 格式修改完成
@agent.entry("testSSH", version="1.0.1")
def my_testSSH(subtask_id, args):
    from encryption.processSSH import stringMatchSSH, procSSHPack, addHostScript
    import thread
    detail = 'SSH是建立在应用层和传输层上的安全协议，专为远程登陆会话和其他网络服务提供安全性的协议。\n' \
             '利用SSH协议可以有效防止远程管理过程中的信息泄露问题。\n' \
             '本测试功能抓取SSH通信数据，检测是否加密。\n'
    array = ['encryption:aes128-ctr', 'Encrypted Packet:']
    if procSSHPack("127.0.0.1"):
        fileName = "encryption/packlog/filterpackSSH"
        try:
            f = open(fileName,"r")
            readbuf = f.readlines()
            f.close()
        except Exception,e:
            print e
        if stringMatchSSH(array):
            print reduce(lambda a, b: a+b, readbuf, '')
            detail += '从抓取的数据包中将加密的协议和加密的数据包解析。\n' \
                      '使用的协议为SSH Protocol\n' \
                      'Encrypted Packet为抓取的加密数据包。\n'
            agent.post_report(subtask_id, 0, 1,
                              brief='done',
                              detail=(detail+'云平台SSH数据传输协议是加密的。').replace('\n', '</br>'),
                              json_data=reduce(lambda a, b: a+b, readbuf, '').replace('\n', '</br>'))
            print "the data is encrypted"
        else:
            agent.post_report(subtask_id, 0, 0,
                              brief='done',
                              detail='云平台SSH数据传输协议是未加密的。'.replace('\n', '</br>'),
                              json_data=reduce(lambda a, b: a+b, readbuf, '').replace('\n', '</br>'))
            print "the data is unencrypted"


# 格式修改完成，返回内容修改完成
@agent.entry("erase_scan", version="1.0.1")
def my_erase_scan(subtask_id, args):
    from sec_storage.disk_erase_detect import get_total_save, do_erase_scan
    import os

    print 'startup erase_scan'
    args = {'path': os.getcwd()+'/sec_storage/test-disk'}
    print args['path']
    disk_path = args['path']

    detail = '磁盘擦出检测检测云平台上将虚拟磁盘擦除时，是否能够根据磁盘的块号读取还原磁盘内容。\n' \
             '虚拟机磁盘一般为RAW格式或者QCOW2格式，可以使用文件系统管理工具对其进行扫描。\n'

    result = get_total_save(disk_path)
    if result == "ERROR":
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='',
                          detail=(detail+'进行磁盘扫描失败。\n').replace('\n', '</br>'),
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
                          detail=(detail+'进行磁盘扫描失败。\n').replace('\n', '</br>'),
                          json_data="进行指定磁盘扫描失败，请检查给定路径是否正确。\n".replace('\n', '</br>'))
    else:
        print 'report', report['result'], 'detail', report['detail']
        agent.post_report(subtask_id,
                          severity=1,
                          result=0,
                          brief='result of erase_scan',
                          detail=(detail+report['detail']).replace('\n', '</br>'),
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

