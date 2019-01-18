# coding: utf-8
# 获取系统信息，保存到json中
import socket, os, re


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    print ip
    return ip


def get_ovrit_version():
    line = os.popen('rpm -qa | grep ovirt-engine-backend').read()
    try:
        version = re.findall(r'([0-9].[0-9])', line)[0]
    except:
        version = '4.2'
    return version

# 获取虚拟机的版本信息
def get_architecture():
    return os.popen('uname -s').read().strip('\r\n')+'-'+os.popen('uname -i').read()

def get_host_version():
    return os.popen('cat /etc/redhat-release').read().replace('\n', '').strip(' ').replace(' ', '-')

def get_sytem_info():
    return {
        'node_ip': get_host_ip(),
        'node_os_version': get_host_version(),
        'node_oVirt_version': get_ovrit_version()
    }


if __name__ == '__main__':
    print get_sytem_info()