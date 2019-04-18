#!/bin/bash

yum install -y wireshark
yum install -y gcc
yum install -y net-tools
yum install -y python-devel
yum install -y libxslt-devel
yum install -y expect
cd /usr/lib/python2.7/site-packages/CloudTest/command/scapy-2.4.2/
python setup.py install
yum install -y install virt-viewer

