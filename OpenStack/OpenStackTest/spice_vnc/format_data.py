# coding: utf-8

from sec_storage.disk_scan import random_list
# 格式化获取的数据
def get_format_data(data, count):
    content = []
    data_list = data.split('\n')[:-3]
    rand_list = random_list(0, len(data_list)-3, min(count, len(data_list)-3))
    for index in rand_list:
        item_data = {}
        split_line = data_list[index].split(' ')
        item_data['encryptedId'] = split_line[0]
        item_data['encryptedData'] = ' '.join(split_line[2:19])
        item_data['decryptedData'] = ' '.join(split_line[20:])
        content.append(item_data)
    return content