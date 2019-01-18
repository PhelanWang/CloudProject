# -*- coding:utf-8 -*-
import socket
import sys
import time

if __name__ == "__main__":

    try:
        ip, port = sys.argv[1].split(":")
        ip_port = (ip, int(port))
    except:
        ip_port = ('localhost', 8001)

    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.settimeout(10)
    sk.connect(ip_port)
    count = 0
    try:
        while count <= 100:
            sk.sendall('This is the cloud platform test message. . .')
            server_reply = sk.recv(1024)
            print server_reply
            count += 1
            time.sleep(2)
    except Exception, e:
        print '测试结束. . .'
        print e

    sk.close()
