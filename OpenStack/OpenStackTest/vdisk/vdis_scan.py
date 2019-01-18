# coding: utf-8

import os


# 检测是否有 qemu-kvm 进程在运行
def is_ready():
    pids = os.popen("pidof qemu-kvm").read().strip('\n').strip(' ')
    print pids
    if pids == '':
        return True
    else:
        return False


# shutdown 会关闭所有的 qemu-kvm 虚拟机进程
def shutdown():
     flag = is_ready()
     while not flag:
         pids = os.popen("pidof qemu-kvm").read().strip('\n').strip(' ').split(' ')
         for pid in pids:
             os.system("kill -9 " + pid)
         flag = is_ready()

# 将 vdisk 文件夹中的 qemu-kvm 替换到 /usr/libexec/qemu-kvm
# 将 /usr/libexec/qemu-kvm 备份为 /usr/libexec/qemu-kvm.back
# 以便旁路出文件数据
def replace_qemu_kvm():
    current_path = os.getcwd() + '/vdisk'
    system_qemu_path = '/usr/libexec'
    result = os.system('mv ' + system_qemu_path + '/qemu-kvm ' + system_qemu_path + '/qemu-kvm.back')
    print result
    result = os.system('cp ' + current_path + '/qemu-kvm ' + system_qemu_path + '/qemu-kvm')
    print result

# 将系统原有 qemu-kvm 还原
# 即将 /usr/libexec/qemu-kvm.back 还原为 /usr/libexec/qemu-kvm
def disreplace_qemu_kvm():
    system_qemu_path = '/usr/libexec'
    result = os.system('mv ' + system_qemu_path + '/qemu-kvm.back ' + system_qemu_path + '/qemu-kvm')
    print result


# 根据关键字，生成以关键字命名的文件
# 在 virtio_blk.log 文件中查找关键字，并将查找到的内容保存到对应文件中
def find_key_word(key_words):
    # 关键字和对应文件的字典
    file_word = {}

    # 创建关键字文件
    for word in key_words:
        os.system('touch /home/qemu/' + word + '.txt')
        file_word[word] = open('/home/qemu/' + word + '.txt', 'w')

    lines = None
    with open('/home/qemu/virtio_blk.log', 'r') as file:
        lines = file.readlines()

    for line in lines:
        for word in key_words:
            if word in line:
                file_word[word].write(line)

    for word in key_words:
        file_word[word].close()


# 分析文件中的关键字
def virtual_disk_scan(args):
    import os
    import time
    if not os.path.exists("/home/qemu/"):
        os.mkdir("/home/qemu/")
        os.system("chown qemu /home/qemu")
        os.system("chmod 777 /home/qemu")
    os.system('rm /home/qemu/virtio_blk.log')

    # 启动测试之前先关闭所有的 qemu-kvm 进程
    print("start shutdown. . .\n")
    shutdown()
    # 然后替换 qemu-kvm
    print("start replace. . .\n")
    replace_qemu_kvm()

    print("Please start vm. . .")
    for i in range(5):
        print(str(i)+' ')
        time.sleep(60)

    print("start shutdown. . .\n")
    shutdown()
    # 等待启动虚拟机，抓取文件，然后关闭所有 qemu-kvm 还原文件
    print("start disreplace. . .\n")
    disreplace_qemu_kvm()


    keywords = args['keyword']
    m_list = keywords

    find_key_word(m_list)

    num = len(m_list)  # 关键字个数

    data = ''
    for file_name in m_list:
        file_path = '/home/qemu/' + file_name + '.txt'
        fo = open(file_path, 'r')
        try:
            file_data = fo.read()
            if file_data == '':
                data += '未找到关键字: ' + file_name + ' 相关内容!\n'
            else:
                data += '找到关键字: ' + file_name + ' 相关内容如下:\n'
                data += file_data + '\n'
        finally:
            fo.close()
            os.system('rm ' + '/home/qemu/' + file_name + '.txt')
    os.system('rm /home/qemu/virtio_blk.log')
    return data
