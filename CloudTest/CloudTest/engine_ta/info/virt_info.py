# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Jul 13 2018, 13:06:57) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
# Embedded file name: /root/git/ovirt/engine_ta/info/virt_info.py
# Compiled at: 2016-05-24 22:01:15

from ovirtsdk.api import API
from ovirtsdk.xml import params
from scapy.all import srp, Ether, ARP, conf
from lib.ta_xml import ta_info_xml
from lib import engine_ta
from time import sleep
import time

def get_engine_api():
    api = None
    eac_data = ta_info_xml.get_engine_api_conf()
    if eac_data == {}:
        return
    try:
#         print eac_data['url'], eac_data['username'], eac_data['password'], eac_data['ca_file']
        api = API(url=eac_data['url'], username=eac_data['username'], password=eac_data['password'], ca_file=eac_data['ca_file'])
    except Exception as e:
        pass

    return api


def delete_vm_by_name(VM_NAME):
    try:
        api = get_engine_api()
        api.vms.get(VM_NAME).delete()
        print 'VM was removed successfully'
        print 'Waiting for VM to be deleted'
        while VM_NAME in [ vm.name for vm in api.vms.list() ]:
            sleep(2)
            print 'searching...'

    except Exception as e:
        print 'Failed to remove VM:\n%s' % str(e)


def get_engine_status():
    api = get_engine_api()
    if api == None:
        return False
    return True


def get_hosts():
    lst_host_ip = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            hostsList = api.hosts.list(max=500)
            for host in hostsList:
                name = host.name
                address = host.address
                state = host.status.state
                lst_host_ip += [[name, address, state]]

        except Exception as e:
            print str(e)

    return lst_host_ip


def get_vm_start_time():
    lst_vm_start_time = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            vmsList = api.vms.list(max=500)
            for instance in vmsList:
                vm_start_time = []
                if instance.status.state == 'up':
                    vm_start_time.append(instance.name)
                    vm_start_time.append(instance.id)
                    vm_start_time.append(instance.get_start_time().ctime())
                    lst_vm_start_time.append(vm_start_time)

        except Exception as e:
            print str(e)

    return lst_vm_start_time


def get_mac_ip(ipscan):
    lst_mac_ip = []
    try:
        ans, unans = srp(Ether(dst='FF:FF:FF:FF:FF:FF') / ARP(pdst=ipscan), timeout=2, verbose=False)
    except Exception as e:
        print str(e)

    for snd, rcv in ans:
        mac_ip = {}
        mac = rcv.sprintf('%Ether.src%')
        ip = rcv.sprintf('%ARP.psrc%')
        mac_ip['mac'] = mac
        mac_ip['ip'] = ip
        lst_mac_ip.append(mac_ip)

    return lst_mac_ip


def get_vm_mac():
    lst_vm_mac = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            vmsList = api.vms.list(max=500)
            for instance in vmsList:
                vm_mac = {}
                if instance.status.state == 'up':
                    vm_info = []
                    vm_info.append(instance.name)
                    vm_info.append(instance.id)
                    vmnics = instance.get_nics().list()
                    for cart in vmnics:
                        vm_info.append(cart.mac.address)

                    vm_mac['vm_name'] = vm_info[0]
                    vm_mac['vm_id'] = vm_info[1]
                    vm_mac['mac'] = vm_info[2]
                    lst_vm_mac.append(vm_mac)

        except Exception as e:
            print str(e)

    return lst_vm_mac


def get_vm_mac_ip():
    """
    Get VM && MAC && IP.
    
    vm_mac_ip = [vm_name,vm_id,mac,ip]
    """
    lst_vm_mac_ip = []
    lst_vm_mac = []
    lst_mac_ip = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        ipscan = ta_info_xml.get_ipscan()
        lst_vm_mac = get_vm_mac()
        lst_mac_ip = get_mac_ip(ipscan)
        for vm_mac in lst_vm_mac:
            vm_name = vm_mac['vm_name']
            vm_id = vm_mac['vm_id']
            mac = vm_mac['mac']
            ip = 'None'
            for mac_ip in lst_mac_ip:
                if mac_ip['mac'] == mac:
                    ip = mac_ip['ip']
                    lst_vm_mac_ip.append([vm_name, vm_id, mac, ip])

            if ip == 'None':
                lst_vm_mac_ip.append([vm_name, vm_id, mac, ip])

    return lst_vm_mac_ip


def get_vm_disks():
    """
    Get VM && Disks.
    
    vm_disk = [vm_name,vm_id,os_type,os_arch,lst_disk]
    disk = [disk_name,disk_alias,disk_format,disk_path]
    """
    lst_vm_disks = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            vmsList = api.vms.list(max=500)
            for instance in vmsList:
                vm_info = []
                vm_info.append(instance.get_name())
                vm_info.append(instance.id)
                vm_info.append(instance.os.get_type())
                vm_info.append(instance.cpu.architecture)
                disks = instance.disks.list()
                for disk in disks:
                    disk_info = []
                    disk_name = disk.get_name()
                    disk_alias = disk.get_alias()
                    disk_id = disk.get_id()
                    disk_format = disk.get_format()
                    storage_id = disk.get_storage_domains().get_storage_domain()[0].get_id()
                    storage = api.storagedomains.get(id=storage_id)
                    storage_path = storage.get_storage().get_path()
                    storage_ip = storage.get_storage().address
                    disk_id = disk.get_id()
                    disk_image_id = disk.get_image_id()
                    disk_path = storage_path + '/' + storage_id + '/images/' + disk_id + '/' + disk_image_id
                    disk_info.append(disk_name)
                    disk_info.append(disk_alias)
                    disk_info.append(disk_id)
                    disk_info.append(disk_image_id)
                    disk_info.append(disk_format)
                    disk_info.append(storage_ip)
                    disk_info.append(disk_path)
                    vm_info.append(disk_info)

                lst_vm_disks.append(vm_info)

        except Exception as e:
            print str(e)

    return lst_vm_disks


def get_vm_disks_for_enc():
    """
    Get VM Disks for encryption.
    
    vm_disk = [vm_name,vm_id,os_type,os_arch,lst_disk]
    disk = [disk_name,disk_alias,disk_id,disk_image_id,disk_format,storage_ip,disk_path]
    """
    lst_vm_disks = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            vmsList = api.vms.list(max=500)
            for instance in vmsList:
                vm_info = []
                vm_info.append(instance.get_name())
                vm_info.append(instance.id)
                vm_info.append(instance.os.get_type())
                vm_info.append(instance.cpu.architecture)
                disks = instance.disks.list()
                for disk in disks:
                    disk_info = []
                    disk_name = disk.get_name()
                    disk_alias = disk.get_alias()
                    disk_id = disk.get_id()
                    disk_format = disk.get_format()
                    storage_id = disk.get_storage_domains().get_storage_domain()[0].get_id()
                    storage = api.storagedomains.get(id=storage_id)
                    storage_path = storage.get_storage().get_path()
                    storage_ip = storage.get_storage().address
                    disk_id = disk.get_id()
                    disk_image_id = disk.get_image_id()
                    disk_path = storage_path + '/' + storage_id + '/images/' + disk_id + '/' + disk_image_id
                    disk_info.append(disk_name)
                    disk_info.append(disk_alias)
                    disk_info.append(disk_id)
                    disk_info.append(disk_image_id)
                    disk_info.append(disk_format)
                    disk_info.append(storage_ip)
                    disk_info.append(disk_path)
                    tmp = vm_info[:]
                    tmp.append(disk_info)
                    lst_vm_disks.append(tmp)

        except Exception as e:
            print str(e)

    return lst_vm_disks


def get_vms_for_mem():
    """
    Get VM For Mem.
    
    m_mem = [vm_name,vm_id,os_type,os_arch,start_time]
    """
    lst_vm_mem = []
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        try:
            vmsList = api.vms.list(max=500)
            for instance in vmsList:
                vm_info = []
                if instance.status.state == 'up':
                    vm_info.append(instance.get_name())
                    vm_info.append(instance.id)
                    vm_info.append(instance.display.address)
                    vm_info.append(instance.os.get_type())
                    vm_info.append(instance.cpu.architecture)
                    vm_info.append(time.mktime(instance.get_start_time().timetuple()))
                    lst_vm_mem.append(vm_info)
                else:
                    vm_info.append(instance.get_name())
                    vm_info.append(instance.id)
                    vm_info.append('None')
                    vm_info.append(instance.os.get_type())
                    vm_info.append(instance.cpu.architecture)
                    vm_info.append('poweroff')
                    lst_vm_mem.append(vm_info)

        except Exception as e:
            print str(e)

    return lst_vm_mem


def test_get_engine_status():
    print 'engine status: [', get_engine_status(), ']'


def test_vm_start_time():
    lst_vm_start_time = get_vm_start_time()
    print lst_vm_start_time


def test_get_hosts():
    hosts = get_hosts()
    print hosts


def test_mac_ip():
    ipscan = ''
    ipscan = ta_info_xml.get_ipscan()
    lst_mac_ip = get_mac_ip(ipscan)
    for mac_ip in lst_mac_ip:
        print mac_ip


def test_vm_mac():
    lst_vm_mac = get_vm_mac()
    for vm_mac in lst_vm_mac:
        print vm_mac


def test_vm_disks():
    vm_disks = get_vm_disks()
    for disk in vm_disks:
        print disk


def test_vm_disks_for_enc():
    vm_disks = get_vm_disks_for_enc()
    for disk in vm_disks:
        print disk


def test_vms_for_mem():
    lst_vm_mem = get_vms_for_mem()
    for vm_mem in lst_vm_mem:
        print vm_mem


def test_engine_api():
    api = get_engine_api()
    if api == None:
        print '[Error] Cannot get engine api'
    else:
        print api
    return


def test_vm_mac_ip():
    lst_vm_mac_ip = []
    lst_vm_mac_ip = get_vm_mac_ip()
    for vm_mac_ip in lst_vm_mac_ip:
        print vm_mac_ip


get_engine_api()
if __name__ == '__main__':
    pass