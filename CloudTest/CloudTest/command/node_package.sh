#!/bin/bash

yum install -y wireshark
yum install -y gcc
yum install -y net-tools
yum install -y libxslt-devel
yum install -y expect
python /root/PycharmProjects/CloudProject/CloudTest/CloudTest/command/scapy-2.4.2/setup.py install
