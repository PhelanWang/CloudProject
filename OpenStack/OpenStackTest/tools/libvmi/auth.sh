# must man config
#saslpasswd2 -a libvirt admin << EOF
#admin
#admin
#EOF

mkdir -p /root/.config/libvirt
cat > /root/.config/libvirt/auth.conf << EOF
[credentials-test]
authname=admin
password=admin

[auth-libvirt-localhost]
credentials=test
EOF

virsh list
