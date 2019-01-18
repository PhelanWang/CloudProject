# coding: utf-8
import os
import pexpect, time
import ConfigParser

# 修改/etc/libvirt/qemu.conf文件，设置根权限
def modify_to_root():
    flag = 0
    with open('/etc/libvirt/qemu.conf', 'rw+') as file:
        data = file.read()
        if data.find('#user') == -1 and data.find('#group') == -1:
            return True
        else:
            data = data.replace('#user', 'user').replace('#group', 'group')
        file.seek(0, 0)
        file.truncate()
        file.write(data)
    os.system('service libvirtd restart')


def execute_command(cmd):
    # print cmd
    child = pexpect.spawn(cmd)
    conf = ConfigParser.ConfigParser()
    conf.read('lib.agent.ctest.conf')
    username = conf.get('virsh', 'username', 'admin')
    password = conf.get('virsh', 'password', 'admin')
    time.sleep(0.1)
    child.sendline(username)
    child.sendline(password)
    # print child.read()
    return child.readlines()


# 获取虚拟机信息
def get_info():
    data = ''
    result = execute_command('virsh list')[4:-1]
    # result = child.readlines()[4:-1]
    # result = child.readlines()[2:-1]
    vms_info = []
    for line in result:
        line_list = list(set(line.strip(' \r\n').split(' ')))
        line_list.sort()
        vms_info.append(line_list)

    for vm_info in vms_info:
        result = execute_command('virsh dommemstat %s' % vm_info[1])[2:]
        # result = child.readlines()[2:]
        result = reduce(lambda a, b: a + b, map(lambda s: s.replace('\r\n', '\n'), result), '虚拟机名称: %s，虚拟机信息如下:\n' % vm_info[2])
        data += result.strip('\r\n')+'\n'
    hyper_infor = 'hypervisor结果如下:\n'
    hyper_infor += os.popen('free -m').read()
    data += hyper_infor
    return data


# 将cirrosx.xml中的IMAGE_PATH替换为正确路径
def replace_image_path(file_path):
    file = open(file_path, 'rw+')
    cirros_path = os.getcwd() + '/vm_trouble/cirros-disk.img'
    # cirros_path = os.getcwd() + '/cirros-disk.img'
    lines = file.readlines()
    for index in range(0, len(lines)):
        if 'source file' in lines[index]:
            lines[index] = '            ' \
                           '<source file=' \
                           '"'+cirros_path+'"' \
                           '/>\n'
            break
    file.seek(0, 0)
    file.truncate()
    file.writelines(lines)

# 启动cirros1和cirros2两台虚拟机
def start_vms():
    cirros_path = os.getcwd() + '/vm_trouble'
    # cirros_path = os.getcwd()
    execute_command('virsh define %s' % cirros_path+'/cirros1.xml')
    execute_command('virsh define %s' % cirros_path+'/cirros2.xml')
    execute_command('virsh start cirros1')
    execute_command('virsh start cirros2')


def copy_image():
    os.system('cp vm_trouble/cirros-disk.img /home/qemu')
    os.system('chown qemu /home/qemu/cirros-disk.img')


def end_vms():
    execute_command('virsh undefine cirros1')
    execute_command('virsh undefine cirros2')


def shutdown_all_vm():
    pids = os.popen('pidof qemu-kvm').read().strip(' \n').split(' ')
    for pid in pids:
        os.system('kill -9 %s' % pid)


def shutdown_one_vm():
    pids = os.popen('pidof qemu-kvm').read().strip(' \n').split(' ')
    os.system('kill -9 %s' % pids[0])


def execute_test():
    shutdown_all_vm()
    # replace_image_path('vm_trouble/cirros1.xml')
    # replace_image_path('vm_trouble/cirros2.xml')
    # modify_to_root()
    copy_image()
    start_vms()
    before_data = get_info()
    shutdown_one_vm()
    after_data = get_info()
    shutdown_one_vm()
    end_vms()
    return before_data, after_data