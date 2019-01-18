# 1. Copy the files in this directory to the domU
# 2. Log into the domU as root.
# 3. cd into the directory with this program, then run make.
#     # yum install kernel kernel-devel
# 4. insmod findoffsets.ko
# 5. if you are logged into the console, you will see the output.
#      otherwise, see /var/log/syslog for the output.
# 6. rmmod findoffsets
# 7. copy the output into your /etc/libvmi.conf file in dom0,
#          be sure to update the domain name and sysmap location.

# cd tools/**
# yum install kernel kernel-devel gcc -y
# make
# insmod findoffsets.ko
# dmesg

#yum install subversion -y
#svn checkout http://pdbparse.googlecode.com/svn/trunk/ pdbparse-read-only
#cd pdbparse-read-only
#python setup.py install
#yum install -y python-pefile
#yum  install -y mscompress cabextract python-pip 
#pip install construct
