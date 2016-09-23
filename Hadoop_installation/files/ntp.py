#!/usr/bin/python
import os,sys
import subprocess
from configobj import ConfigObj
path = os.getcwd()
path = sys.argv[1]

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
