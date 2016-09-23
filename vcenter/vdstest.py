import atexit
import warnings
import requests
from pyVmomi import vim, vmodl
from pyVim import connect
from requests.exceptions import ConnectionError
from datetime import timedelta, datetime
from decimal import *
import ssl
import json
import argparse
import time
import datetime
import ConfigParser

def check_for_stop():
    config = ConfigParser.ConfigParser()
    config.read("file.conf")
    stop = config.get('params','stop')
    if (stop=="true"):
        print ("Stop issued")
        exit()
    else:
        return "false"

def connection(args):
    context = None
    '''
    Disabling SSL certificate verification
    '''
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
    except AttributeError:
        rget = requests.get
        requests.get = lambda obj, *args,**kwargs: rget(obj,verify=False)
        requests.packages.urllib3.disable_warnings()

    '''
    Connect to a VCenter
    '''
    serv_details = {'host':args.hostname, 'user':args.username, 'passwd':args.password, 'port':args.port}
    si = connect.SmartConnect(host=serv_details['host'],user=serv_details['user'],pwd=serv_details['passwd'],port=serv_details['port'], sslContext=context)
    atexit.register(connect.Disconnect, si)
    print 'Connection successful\n'
    return si

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--hostname', help='IP of Vcenter', required=True)
    parser.add_argument('-u','--username', help='Username of Vcenter', required=True)
    parser.add_argument('-p','--password', help='Password of Vcenter', required=True)
    parser.add_argument('-o','--port', help='Port number of Vcenter', required=True)
    parser.add_argument('-i', '--interval', help='Interval to sleep in minutes', required=True)
    parser.add_argument('-t', '--tag', help='Tag for the run', required=True)
    args = parser.parse_args()

    while(1):
        stop = check_for_stop()
        if(stop=="false"):
            si = connection(args)

            '''
            Get all Datastores
            '''    
            content = si.RetrieveContent()
            viewType = [vim.Datastore]
            objView = content.viewManager.CreateContainerView(content.rootFolder,viewType,True)
            print "Results Calculation started.."
            payload = {}
            ds_json = []
            ts = time.time()
            payload['timestamp'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
            payload['Tag'] = args.tag
            for ds in objView.view:
                ds_dict = {}
                ds_dict['Name'] = ds.summary.name
                ds_dict['Location'] = ds.summary.url
                ds_dict['Type'] = ds.summary.type
                ds_dict['Capacity(TB)'] = str(float(ds.summary.capacity)/1024/1024/1024/1024)
                ds_dict['Free_Space(TB)'] = str(float(ds.summary.freeSpace)/1024/1024/1024/1024)
                ds_dict['Number_of_vms'] = str(len(ds.vm))
                ds_dict['Number_of_hosts'] = str(len(ds.host))
                host_dict=[]
                for host in ds.host:
                    host_json = {}
                    host_json["Host_Name"]=str(host.key.name)
                    host_dict.append(host_json)
                ds_dict['Hosts'] = host_dict
                ds_json.append(ds_dict)

            payload['Datastores'] = ds_json
            print "Completed.."
            #print json.dumps(payload)
            url = "http://localhost:9200/vcenter/datastore"
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(payload),headers=headers)
            print "Results sent to elasticsearch"
            connect.Disconnect(si)
            print "Connection revoked"
        print "Sleeping for interval of " + str(int(args.interval)) +" minute(s)."
        time.sleep(int(args.interval)*60)

if __name__ == "__main__":
    main()

