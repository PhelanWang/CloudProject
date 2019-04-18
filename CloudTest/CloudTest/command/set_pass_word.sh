#!/usr/bin/expect

spawn saslpasswd2 -a libvirt admin

expect "Password:"
send "admin\r"

expect "Again (for verification):"
send "admin\r"

interact
