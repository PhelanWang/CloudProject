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


def get_openstack_version():
    try:
        line = os.popen('nova-manage version').read()
        version = '-'.join(line.strip('\n').split(' '))
    except:
        version = 'unknow'
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
        'node_openStack_version': get_openstack_version()
    }


# 找出所有磁盘路径
def find_all_disk():
    import os, json
    vdisk = []
    disk_infos = os.popen('find /var/lib/nova/instances -name disk.info').readlines()
    for disk_info in disk_infos:
        print disk_info
        disk_dict = os.popen('cat ' + disk_info.strip('\n')).read().strip('\n')
        disk_dict = json.loads(disk_dict)
        print disk_dict.keys()[0], disk_dict.values()[0]
        id = disk_dict.keys()[0].split('/')[-2]
        vdisk.append([id, id, 'other', 'x86_64', [id, id, id, id, disk_dict.values()[0], get_host_ip(), disk_dict.keys()[0]]])
    vdisk = {'disk': [vdisk, get_host_ip(), 9099]}
    return vdisk

def get_openstack_disk():
    import os, json
    vdisk = []
    disks = os.popen("lvscan | grep /dev/cinder-volumes/volume- | awk '{print $2}'").readlines()
    for disk in disks:
        print('+', 'disk:', disk, '+')
        disk_path = disk.replace("\n", '').replace("'", '')
        disk_id = '-'.join(disk.split('/')[-1].split('-')[1:]).replace("\n", '').replace("'", '')
        vdisk.append([disk_id, disk_id, 'other', 'x86_64',
                      [disk_id, disk_id, disk_id, disk_id, disk_path,
                       get_host_ip(), disk_path]])

    vdisk = {'disk': [vdisk, get_host_ip(), 9099]}
    print vdisk
    return vdisk


def get_nfs_disk():
    import os, json
    mount_path = os.popen('showmount -e').read()
    disk_path = mount_path.split('\n')[-2].split(' ')[0]
    disks = os.popen('ls '+disk_path).read().split('\n')
    vdisk = []
    for disk in disks[:-1]:
        vdisk.append([disk, disk, 'other', 'x86_64',
                      [disk, disk, disk, disk, disk_path+'/'+disk,
                       get_host_ip(), disk_path+'/'+disk]])
    vdisk = {'disk': [vdisk, get_host_ip(), 9099]}
    print(vdisk)
    return vdisk


def get_default_disk():
    vdisk = {'disk':
     [
         [
             [
                 'default',
                 'default',
                 'other',
                 'x86_64',
                 [
                     'default',
                     'default',
                     'default',
                     'default',
                     'qcow2',
                     get_host_ip(),
                     os.getcwd()+'/test.qcow2']
             ]
         ],
         get_host_ip(), 9099
     ]
    }
    return vdisk


if __name__ == '__main__':
    print get_openstack_disk()

{'disk':
    [
        [
            ['TestVM1', # ??????
             '6bfe1141-d081-4d28-876e-7c4a3c256e0a', # ????ID
             'other',
             'x86_64',
             ['TestVM1_Disk1',
              'TestVM1_Disk1',
              '75e594f8-8509-41ef-ab6e-589cf649a117',
              '9219c3cf-e04d-4334-9a1f-53c6ac74a2ac',
              'raw', # ????
            '192.168.1.106',
              '/root/share/3cc6ec36-2cd5-4663-b6b2-c472e2704789/images/75e594f8-8509-41ef-ab6e-589cf649a117/9219c3cf-e04d-4334-9a1f-53c6ac74a2ac'  # ???????path?
              ]
             ],
            ['TestVM2',
             'c2c9f71c-dce2-4af5-94ef-d6ab4da02827',
             'other',
             'x86_64',
              ['TestVM2_Disk1',
               'TestVM2_Disk1',
               'bb52434b-3ab5-4e86-bd83-7d5ea64f66d6',
               '63ea7464-6dd5-42ca-86d3-37124969f9bb',
               'raw',
               '192.168.1.106',  # NodeIP ?????IP??
               '/root/share/3cc6ec36-2cd5-4663-b6b2-c472e2704789/images/bb52434b-3ab5-4e86-bd83-7d5ea64f66d6/63ea7464-6dd5-42ca-86d3-37124969f9bb'
# ???????
               ]
             ]
         ],
        '192.168.1.117', 8085 #Engine?Node
    ]
}

{'disk':
     [
         [
             [
                 u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                 u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                 'other',
                 'x86_64',
                 [
                     u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                     u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                     u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                     u'b9c4bfa3-7546-41f3-b008-f6d9f67cf42c',
                     u'qcow2',
                     '192.168.1.127',
                     u'/var/lib/nova/instances/b9c4bfa3-7546-41f3-b008-f6d9f67cf42c/disk'
                 ]
             ],
             [
                 u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                 u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                 'other',
                 'x86_64',
                 [
                     u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                     u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                     u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                     u'0c4d5747-6263-4931-ae39-9c7bf7c6f871',
                     u'qcow2',
                     '192.168.1.127',
                     u'/var/lib/nova/instances/0c4d5747-6263-4931-ae39-9c7bf7c6f871/disk']
             ]
         ],
         '192.168.1.127', 9099
     ]
}

{'disk':
     [
         [
             [
                 'default',
                 'default',
                 'other',
                 'x86_64',
                 [
                     'default',
                     'default',
                     'default',
                     'default',
                     'qcow2',
                     get_host_ip(),
                     os.getcwd()+'/ubuntu.qcow2']
             ]
         ],
         get_host_ip(), 9099
     ]
}
