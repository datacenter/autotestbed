import requests
import json

import datetime
logstash_host = 'localhost'

def get_formated_date(date_val):
    return str(datetime.datetime.fromtimestamp(int(str(date_val)[:10])).strftime('%B %d %Y %H:%M:%S'))

def get_http_response(url, data='{}'):  
    #headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    rest_data_dict = {}
    try:
        response = requests.get(url, data=data)
        if response.ok:
            rest_data_dict = json.loads(response.content)
        else:
            pass#response.raise_for_status()
    except:
        print 'Error connecting :', url
    return rest_data_dict

def send_to_logstash(pl_logger, msg, extra, stat_type, plugin_name, dtype=''):
    if dtype:
        new_dict = {}
        for kval, vval in extra.items():
            new_dict[dtype + '_' + kval] = vval
        extra = new_dict
    extra['stat_type'] = stat_type
    extra['plugin'] = plugin_name
    pl_logger.info(msg, extra=extra)
    return 

def get_cmd_res(hostname, uname, pwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=uname, password=pwd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdoutsp_ar = stdout.read().split('\n')
    return stdoutsp_ar

def dd(extra):
    print extra
    for k, v in sorted(extra.items(), key=lambda extra:(extra[0], extra[1])):
        print '"'+k+'"', ':', '"'+str(v) + '",'
