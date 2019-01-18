# -*- coding:utf-8 -*-

import socket
import sys


if __name__ == "__main__":
    # ip, port = sys.argv[1].split(":")
    # ip_port = (ip, int(port))

    ip_port = ('0.0.0.0', 8001)
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.bind(ip_port)

    print 'server waiting...'
    count = 0
    try:
        while count <= 100:
            client_data, address = sk.recvfrom(1024)
            print client_data, address
            sk.sendto('This is the cloud platform test message. . .', address)
            count += 1
    except Exception, e:
        print '测试结束. . .'

    sk.close()