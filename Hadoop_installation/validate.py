#!/usr/bin/python
import os,sys
import subprocess

cldb = []
nfs = []
webserver = []
fileserver = []
jobtracker = []
resourcemanager = []
historyserver = []
nodemanager = [] 
tasktracker = []

data  = open("/etc/ansible/hosts",'r')
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
        if line.strip() == "[mapr-nfs]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    nfs.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-webserver]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                   webserver.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-fileserver]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                   fileserver.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-jobtracker]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    jobtracker.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-resourcemanager]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    resourcemanager.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-historyserver]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    historyserver.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-nodemanager]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    nodemanager.append(line.strip('\n').split(" ")[0])

data  = open("/etc/ansible/hosts",'r')
for line in data:
        if line.strip() == "[mapr-tasktracker]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                    tasktracker.append(line.strip('\n').split(" ")[0])
print "===================================================================================================="

for ip in cldb:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", ip, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("CLDB"):
            value = line.split()
            if value[-3] == '0':
                print "  *  CLDB on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  CLDB on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  CLDB on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  CLDB on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  CLDB on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  CLDB on %s is Stand by." %(ip)

    
#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in nfs:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", ip, cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("Gateway"):
            value = line.split()
            if value[-4] == '0':
                print "  *  NFS on %s is Not configured." %(ip)
            if value[-4] == '1':
                print "  *  NFS on %s is Configured." %(ip)
            if value[-4] == '2':
                print "  *  NFS on %s is Running." %(ip)
            if value[-4] == '3':
                print "  *  NFS on %s is Stopped." %(ip)
            if value[-4] == '4':
                print "  *  NFS on %s is Failed." %(ip)
            if value[-4] == '5':
                print "  *  NFS on %s is Stand by." %(ip)



#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in webserver:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("Webserver"):
            value = line.split()
            if value[-3] == '0':
                print "  *  Webserver on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  Webserver on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  Webserver on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  Webserver on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  Webserver on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  Webserver on %s is Stand by." %(ip)


#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in fileserver:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("FileServer"):
            value = line.split()
            if value[-3] == '0':
                print "  *  FileServer on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  FileServer on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  FileServer on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  FileServer on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  FileServer on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  FileServer on %s is Stand by." %(ip)


#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in jobtracker:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("JobTracker"):
            value = line.split()
            if value[-3] == '0':
                print "  *  JobTracker on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  JobTracker on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  JobTracker on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  JobTracker on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  JobTracker on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  JobTracker on %s is Stand by." %(ip)


#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in resourcemanager:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("ResourceManager"):
            value = line.split()
            if value[-3] == '0':
                print "  *  ResourceManager on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  ResourceManager on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  ResourceManager on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  ResourceManager on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  ResourceManager on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  ResourceManager on %s is Stand by." %(ip)

#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in historyserver:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("JobHistoryServer"):
            value = line.split() 
            if value[-3] == '0':
                print "  *  JobHistoryServer on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  JobHistoryServer on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  JobHistoryServer on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  JobHistoryServer on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  JobHistoryServer on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  JobHistoryServer on %s is Stand by." %(ip)

#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in nodemanager:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("NodeManager"):
            value = line.split() 
            if value[-3] == '0':
                print "  *  NodeManager on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  NodeManager on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  NodeManager on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  NodeManager on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  NodeManager on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  NodeManager on %s is Stand by." %(ip)


#print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
print "===================================================================================================="
for ip in tasktracker:
    cmd = "maprcli service list -node " + ip
    ssh = subprocess.Popen(["ssh", str(ip), cmd],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    for line in result:
        line =line.strip()
        if line.endswith("TaskTracker"):
            value = line.split() 
            if value[-3] == '0':
                print "  *  TaskTracker on %s is Not configured." %(ip)
            if value[-3] == '1':
                print "  *  TaskTracker on %s is Configured." %(ip)
            if value[-3] == '2':
                print "  *  TaskTracker on %s is Running." %(ip)
            if value[-3] == '3':
                print "  *  TaskTracker on %s is Stopped." %(ip)
            if value[-3] == '4':
                print "  *  TaskTracker on %s is Failed." %(ip)
            if value[-3] == '5':
                print "  *  TaskTracker on %s is Stand by." %(ip)

print "===================================================================================================="
