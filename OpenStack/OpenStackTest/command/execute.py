# coding: utf-8

import os
import sys


convention_used = '''
使用方式
openstack_start --client_ip=xxx.xxx.xxx.xx
client_ip: 客户端的ip地址
'''


def process_parameter(param=None):
    try:
        param = (''.join(param[1:])).split('--')
        param_dict = {}
        if len(param) >= 1:
            for item in param:
                if '=' in item:
                    (key, value) = item.split('=')
                    param_dict[key] = value
            if param_dict.has_key('client_ip'):
                return param_dict
            else:
                sys.exit(0)
        else:
            sys.exit(0)
    except:
        print(convention_used)
        sys.exit(0)


def not_install():
    lock_file = open('./lock_file.txt', 'rw+')
    flag = lock_file.read()
    if flag == '0':
        print('init. . .\n')
        flag = True
    else:
        print('not init. . .\n')
        flag = False
    lock_file.seek(0)
    lock_file.write('1')
    lock_file.close()
    return flag


def install_packages():
    os.chdir('/usr/lib/python2.7/site-packages/OpenStackTest/command')
    # if not_install():
    print("初始化安装依赖包. . .\n")
    packages = ['pexpect==2.4', 'dnspython==1.12.0', 'Flask==1.0.2', 'Flask-RESTful==0.3.6', 'numpy']
    for item in packages:
        os.system('pip install --no-index -f ./packages '+item)


def init():
    # 创建目录并授权
    os.system('mkdir /home/qemu')
    os.system('chown qemu /home/qemu')
    os.system('setenforce 0')
    # 打开端口
    os.system('firewall-cmd --zone=public --add-port=9099/tcp --permanent')
    os.system('firewall-cmd --zone=public --add-port=8001/udp --permanent')
    os.system('firewall-cmd --reload')
    # 拷贝client_python2.py到/home/qemu目录下
    os.system('/usr/lib/python2.7/site-packages/OpenStackTest/command/client_python2.py /home/qemu')
    install_packages()


def write_param(param_dict):
    import ConfigParser
    os.chdir('/usr/lib/python2.7/site-packages/OpenStackTest')
    conf = ConfigParser.ConfigParser()
    conf.read('lib.agent.ctest.conf')
    conf.set('network', 'server-base', 'http://'+param_dict['client_ip']+':8000')
    conf.write(open('lib.agent.ctest.conf', 'w'))


def start_openstack_test():
    param_dict = process_parameter(sys.argv)
    write_param(param_dict)
    sys.path.append('/usr/lib/python2.7/site-packages/OpenStackTest')
    os.chdir('/usr/lib/python2.7/site-packages/OpenStackTest')
    os.system('python agent_loader.py')



