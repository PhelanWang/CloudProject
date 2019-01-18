# coding: utf-8
import os
# 将a文件的字符去出在b文件中执行查找操作。如果存在就直接写入文件
def find_same():
    # 取出a文件并直接调用
    id1_file = open('./v_id1', 'r')
    id2_file = open('./v_id2', 'r')
    # 每次读取一行保存到s中；
    # 进行判断
    # 找出两个内存页面的相同地址
    if(os.path.exists("./v_final")):
        open('./v_final', 'a').truncate(0)
    else:
        os.system("touch ./v_final")
    final_file = open('./v_final', 'a')
    id2_text = id2_file.read()
    id2_file.close()
    j = 0
    print 'start compare. . .'
    import time
    start = time.time()

    for line in id1_file.readlines():
        if (id2_text.find(line) != -1):
            final_file.write(line)

    print 'end compare. . .'
    end = time.time()
    print (end - start) / 60
    id1_file.close()
    final_file.close()

# find_same()
