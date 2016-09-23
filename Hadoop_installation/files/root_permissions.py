#!/usr/bin/python
import os
import subprocess
jobtracker_ip = None
with open('/etc/ansible/hosts', 'r') as f:
    for line in f:
        if line.startswith("[mapr-jobtracker]\n"):
            for i in range(1):
                jobtracker_ip = f.next()

ip = jobtracker_ip.strip()
cmd = "/opt/mapr/bin/maprcli acl edit -type cluster -user root:fc"
ret = subprocess.call(["ssh", ip, cmd]);

