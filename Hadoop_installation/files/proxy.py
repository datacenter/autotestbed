#!/usr/bin/python
import sys
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
