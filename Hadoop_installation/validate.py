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

def get_service_ip_list(hostfile,service_name,service_ip_list):

    data  = open(hostfile,'r')
    for line in data:
            if line.strip() == "["+service_name+"]":
                copy = True
            elif line.startswith("["):
                copy = False
            elif copy:
                if not line in ['\n', '\r\n']:
                    if not line.startswith("#"):
                        service_ip_list.append(line.strip('\n').split(" ")[0])

get_service_ip_list("/etc/ansible/hosts","mapr-cldb",cldb)
get_service_ip_list("/etc/ansible/hosts","mapr-nfs",nfs)
get_service_ip_list("/etc/ansible/hosts","mapr-webserver",webserver)
get_service_ip_list("/etc/ansible/hosts","mapr-fileserver",fileserver)
get_service_ip_list("/etc/ansible/hosts","mapr-jobtracker",jobtracker)
get_service_ip_list("/etc/ansible/hosts","mapr-resourcemanager",resourcemanager)
get_service_ip_list("/etc/ansible/hosts","mapr-historyserver",historyserver)
get_service_ip_list("/etc/ansible/hosts","mapr-nodemanager",nodemanager)
get_service_ip_list("/etc/ansible/hosts","mapr-tasktracker",tasktracker)

print "===================================================================================================="

def get_service_status(service_ip_list,service_name):

    for ip in service_ip_list:
        cmd = "maprcli service list -node " + ip
        ssh = subprocess.Popen(["ssh", ip, cmd],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        for line in result:
            line =line.strip()
            if line.endswith(service_name):
                value = line.split()
                if value[-3] == '0':
                    print "  * ",service_name,"on %s is Not configured." %(ip)
                if value[-3] == '1':
                    print "  * ",service_name,"on %s is Configured." %(ip)
                if value[-3] == '2':
                    print "  * ",service_name,"on %s is Running." %(ip)
                if value[-3] == '3':
                    print "  * ",service_name,"on %s is Stopped." %(ip)
                if value[-3] == '4':
                    print "  * ",service_name,"on %s is Failed." %(ip)
                if value[-3] == '5':
                    print "  * ",service_name,"on %s is Stand by." %(ip)

    
    #print tasktracker, nodemanager, historyserver, resourcemanager, jobtracker, fileserver, webserver, nfs, cldb
    print "===================================================================================================="

get_service_status(cldb,"CLDB")
get_service_status(nfs,"NFS Gateway")
get_service_status(webserver,"Webserver")
get_service_status(fileserver,"FileServer")
get_service_status(jobtracker,"JobTracker")
get_service_status(resourcemanager,"ResourceManager")
get_service_status(historyserver,"JobHistoryServer")
get_service_status(nodemanager,"NodeManager")
get_service_status(tasktracker,"TaskTracker")

