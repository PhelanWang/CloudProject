#!/bin/sh
echo $pwd
tshark -i any -n -f "src port $1" -d "tcp.port==$1,vnc" -a duration:120 -w data.cap&&
hexdump -C data.cap > spice.txt
