#!/bin/bash

user=$1
ip=$2
password=$3
sshpass -p $3 ssh  -o "StrictHostKeyChecking no" $user@$ip  << EOF
scope chassis
scope network-adapter L
show mac-list
EOF

