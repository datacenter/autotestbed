#!/usr/bin/python
import os,sys
import subprocess
jobtracker_ip = None
license_path = sys.argv[1]
cluster_name = sys.argv[2]
with open('/etc/ansible/hosts', 'r') as f:
    for line in f:
        if line.startswith("[mapr-jobtracker]\n"):
            for i in range(1):
                jobtracker_ip = f.next()

ip = jobtracker_ip.strip()
print ip
cmd = "scp " + license_path + " " + ip + ":/tmp/license"
os.system(cmd)

cmd2 = "maprcli license add  -cluster " + cluster_name  +  " -license /tmp/license  -is_file true"
subprocess.call(["ssh", ip, cmd2]);
