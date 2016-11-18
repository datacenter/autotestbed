#!/usr/bin/python
import re,os,sys
import subprocess
from configobj import ConfigObj

copy = False
cldb = []
zookeeper = []
history = []
rm = []

def get_service_ips(ser_ip_list, ser_name):
    data  = open("/etc/ansible/hosts",'r')
    for line in data:
        if line.strip() == "[" + ser_name + "]":
            copy = True
        elif line.startswith("["):
            copy = False
        elif copy:
            if not line in ['\n', '\r\n']:
                if not line.startswith("#"):
                   ser_ip_list.append(line.strip('\n').split(" ")[0])

get_service_ips(cldb, 'mapr-cldb')
get_service_ips(zookeeper, 'mapr-zookeeper')
get_service_ips(rm, 'mapr-resourcemanager')
get_service_ips(history, 'mapr-historyserver')


mcldb =  ','.join(cldb)
mzoo = ','.join(zookeeper)
mhist = ','.join(history)
mrm =  ','.join(rm)

cluster_name = sys.argv[2]
cmd  = "/opt/mapr/server/configure.sh -C " + mcldb + " -Z " + mzoo + " -RM " + mrm + " -HS " + mhist + " -N " + cluster_name
path = sys.argv[1]
cmd1 = "echo " + cmd + " > " + path + "/files/cmd.sh"
os.system(cmd1)
cmd2 = "chmod 777 " + path + "/files/cmd.sh"
os.system(cmd2)

################################################################################################

#path = os.getcwd()
#print path
path = sys.argv[1]
print path

file1 = path+"/settings.cfg"
config = ConfigObj(file1)
jobtracker_ip = None
with open('/etc/ansible/hosts', 'r') as f:
    for line in f:
        if line.startswith("[ntp-server]\n"):
            for i in range(1):
                jobtracker_ip = f.next()

ip = jobtracker_ip.strip()
print config['details']['network']
network = config['details']['network']
mask =  config['details']['mask']

file2 = path+"/files/ntp_server_temp.conf"
ntp_tmp = open(file2,'r')
file3 = path+"/files/ntp_server.conf"
ntp_server = open(file3,'w')
for line in ntp_tmp:
   if line.startswith("server "):
      line = "server " + ip + "\nserver  127.127.1.0 \nfudge   127.127.1.0 stratum 10 \n"

   if line.startswith("restrict 172.31.216.0"):
      line = "restrict "+ network + " mask " + mask  +" nomodify notrap" + "\n"
   ntp_server.write(line)

file4 = path+"/files/ntp_client_tmp.conf"
ntp_client_tmp = open(file4,'r')
file5 = path+"/files/ntp_client.conf"
ntp_client = open(file5,'w')
for line in ntp_client_tmp:
   if line.startswith("server "):
      line = "server " + ip + "\n"
   ntp_client.write(line)

cmd = "echo ntpdate -u " + ip + " > "+ path +"/files/ntp_sync.sh"
cmd1 = "chmod 777 " + path +"/files/ntp_sync.sh"
os.system(cmd)
os.system(cmd1)

################################################################################################
proxy_ip = None
with open('/etc/ansible/hosts', 'r') as f:
    for line in f:
        if line.startswith("[squid3]\n"):
            for i in range(1):
               proxy_ip = f.next()

#Acquire::http::proxy "http://192.168.0.46:8888";                
proxy_string = 'Acquire::http::proxy "http://' +  proxy_ip.strip() + ':3128";'
path = sys.argv[1] + "/files/apt.conf"
f1 = open(path,'w')
f1.write(proxy_string)

