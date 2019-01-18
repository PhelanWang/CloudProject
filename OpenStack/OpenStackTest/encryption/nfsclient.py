#!/usr/bin/python
import socket
import sys
import time
def sendmessage(msg):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    host='127.0.0.1'
    port=8888
    try:
        time.sleep(2)
        s.sendto(msg,(host,port))
        d=s.recvfrom(1024)
        reply=d[0]
        addr=d[1]
        return  reply
    except socket.error,msg:
        print 'Error Code:'+str(msg[0])+'Message'+msg[1]
        sys.exit()
    finally:
        s.close()

if __name__ == "__main__":
    # ss = ["adasfasf","asdasdas","abcd","eeee","test"]
    # fp = open('nfscap')
    # proof = ""
    # count = 0;
    # for it in fp:
    #     if it.find('testnfs')!=-1:
    #         fp.seek(count)
    #         break
    #     count +=len(it)
    # for y in range(10):
    #     proof+= fp.readline()
    # print proof
    print sendmessage('test#filename#this is a test!')