#!/usr/bin/python
import re,os
import sys
data  = open("/etc/ansible/hosts",'r')
copy = False
cldb = []
zookeeper = []
history = []
rm = []
for line in data:
        if line.strip() == "[mapr-cldb]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                   cldb.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-zookeeper]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                   zookeeper.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-resourcemanager]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    rm.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-historyserver]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    history.append(line.strip('\n').split(" ")[0])


mcldb =  ','.join(cldb)
mzoo = ','.join(zookeeper)
mhist = ','.join(history)
mrm =  ','.join(rm)

cluster_name = sys.argv[1]
cmd  = "/opt/mapr/server/configure.sh -C " + mcldb + " -Z " + mzoo + " -RM " + mrm + " -HS " + mhist + " -N " + cluster_name
path = sys.argv[2]
cmd1 = "echo " + cmd + " > " + path + "/files/cmd.sh"
os.system(cmd1)
cmd2 = "chmod 777 " + path + "/files/cmd.sh"
os.system(cmd2)

