#!/usr/bin/python
import socket
import sys
import os

host='127.0.0.1'
port=8888

try:
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error,msg:
    print 'Failed to create socket.Error Code:'+str(msg[0])+'Message'+msg[1]
    sys.exit()

try:
    s.bind((host,port))
except socket.error,msg:
    print 'Failed to create socket.Error Code:'+str(msg[1])+'Message'+msg[1]
    sys.exit()

print "start nfs agent"
while True:
    d=s.recvfrom(1024)
    data=d[0]
    addr=d[1]
    if not data:
        continue
    testlist = data.split('#')
    action = testlist[0]
    filename= testlist[1]
    test_text = testlist[2]
    if action == "test":
        if os.path.exists(filename):
            os.remove(filename)
        os.mknod(filename)
        fp = open(filename,'w')
        try:
            print test_text
            fp.write(test_text)
        except Exception,e:
            pass
        finally:
            fp.close()
        reply = 'success'
        s.sendto(reply,addr)
    else:
        continue
s.close()

