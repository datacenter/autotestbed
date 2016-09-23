#!/bin/bash

user=$1
ip=$2
password=$3
boot_mode=$4
sshpass -p $3 ssh -o "StrictHostKeyChecking no" $user@$ip  << EOF
scope bios
scope boot-device $boot_mode
set order 1
commit
EOF

#this test