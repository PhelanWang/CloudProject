# coding: utf-8

import os
import sys


convention_used = '''
使用方式
node_start/engine_start --client_ip=xxx.xxx.xxx.xxx
engine端使用engine_start, node端使用node_start
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
                param_dict['user_name'] = 'admin'
                param_dict['pass_word'] = 'admin'
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


def install_packages(type):
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/command')

    print("初始化安装依赖包. . .\n")
    packages = ['pexpect==2.4', 'dnspython==1.12.0', 'Flask==1.0.2', 'Flask-RESTful==0.3.6',
                'numpy', 'ovirt-engine-sdk-python==4.2.7', 'boto']
    for item in packages:
        os.system('pip install --no-index -f ./packages '+item)


def node_init():
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/command/')
    os.system('./node_package.sh')
    # 设置密码
    os.system('./set_pass_word.sh')
    init('node')


def engine_init():
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/command/')
    os.system('./engine_package.sh')
    init('engine')


def init(type):
    # 创建目录并授权
    os.system('mkdir /home/qemu')
    os.system('chown qemu /home/qemu')
    os.system('setenforce 0')
    # 打开端口
    os.system('firewall-cmd --zone=public --add-port=9099/tcp --permanent')
    os.system('firewall-cmd --zone=public --add-port=8001/udp --permanent')
    os.system('firewall-cmd --reload')

    # 拷贝client_python2.py到/home/qemu目录下
    os.system('cp /usr/lib/python2.7/site-packages/CloudTest/command/client_python2.py /home/qemu')
    install_packages(type)


def write_param(param_dict, node_name):
    import ConfigParser
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/'+node_name)
    conf = ConfigParser.ConfigParser()
    conf.read('lib.agent.ctest.conf')
    conf.set('network', 'server-base', 'http://'+param_dict['client_ip']+':8000')
    conf.set('virsh', 'username', param_dict['user_name'])
    conf.set('virsh', 'password', param_dict['pass_word'])
    conf.write(open('lib.agent.ctest.conf', 'w'))


def start_node():
    param_dict = process_parameter(sys.argv)
    write_param(param_dict, 'node_ta')
    sys.path.append('/usr/lib/python2.7/site-packages/CloudTest/node_ta')
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/node_ta')

    os.system('python agent_loader.py')


def start_engine():
    param_dict = process_parameter(sys.argv)
    write_param(param_dict, 'engine_ta')
    sys.path.append('/usr/lib/python2.7/site-packages/CloudTest/engine_ta')
    os.chdir('/usr/lib/python2.7/site-packages/CloudTest/engine_ta')

    os.system('python agent_loader.py')


