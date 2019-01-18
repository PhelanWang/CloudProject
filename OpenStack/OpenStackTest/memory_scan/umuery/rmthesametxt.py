#coding:utf-8
import os
ciku = open(r'v_final','r')
xieci = open(r'v_result','a')
## add code##

######
cikus = ciku.readlines()
list2={}.fromkeys(cikus).keys()
i = 1
for line in list2:
	if line[0] != ',':
		i += 1
		xieci.writelines(line)
####写入分隔字符
xieci.writelines("两台虚拟机的共同的地址空间为:")
xieci.writelines("\n")
xieci.close()

