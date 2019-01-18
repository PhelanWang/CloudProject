#!/usr/bin/env python
import socket
import sys
import time
import unsecurity_service

def sendmessage(msg):
	try:
		s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	except socket.error:
		print 'Failed to create socket'
		sys.exit()

	host='localhost'
	port=8888

	while True:
		try:
			time.sleep(2)
			s.sendto(msg,(host,port))
			d=s.recvfrom(1024)
			reply=d[0]
			addr=d[1]
			print 'Server reply:'+reply
			if unsecurity_service.get_captured():
				break
		except socket.error,msg:
			print 'Error Code:'+str(msg[0])+'Message'+msg[1]
			sys.exit()
	unsecurity_service.set_captured(False)
	exit(0)