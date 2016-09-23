import atexit
import warnings
from pyVmomi import vim, vmodl
from pyVim import connect
from requests.exceptions import ConnectionError
import requests
import ssl
import json
import time
import datetime
import ConfigParser
import argparse

def check_for_stop():
    config = ConfigParser.ConfigParser()
    config.read("file.conf")
    stop = config.get('params','stop')
    if (stop=="true"):
        print ("Stop issued")
        exit()
    else:
        return "false"

class VCenterServerMonitor:
    def __init__(self, vc_details):
        self.vcsa_ip = vc_details['host']
        self.vcsa_user = vc_details['user']
        self.vcsa_passwd = vc_details['passwd']
        self.vcsa_port = vc_details['port']

    def connect_vc(self):
        #warnings.simplefilter('ignore')
        context = None
        try:
            # Disabling SSL certificate verification
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_NONE
        except AttributeError:
            rget = requests.get
            requests.get = lambda obj, *args,**kwargs: rget(obj,verify=False)
            requests.packages.urllib3.disable_warnings()

        try:
            self.si = connect.SmartConnect(host=self.vcsa_ip,user=self.vcsa_user,pwd=self.vcsa_passwd,port=self.vcsa_port,sslContext=context)
            atexit.register(connect.Disconnect, self.si)
        except vim.fault.InvalidLogin:
            raise VCConfigError("Error in connecting to vCenter Server: Invalid Username and Password Combination")
        except ConnectionError as e:
            print ("Connection Error: Could not connect to vCenter Server")
            exit()
        print 'Connection Successful\n'

    def list_datacenters(self):
        installed_dcs = []
        child_entity = self.si.content.rootFolder.childEntity
        installed_dcs.extend([child_entity[i].name for i in range(0, len(child_entity))])
        return installed_dcs

    def get_datacenter(self, dcName):
        folder = self.si.content.rootFolder
        if folder is not None and isinstance(folder, vim.Folder):
            for dc in folder.childEntity:
                if dc.name == dcName:
                    return dc
        return None

    def list_clusters(self, datacenter=None):
        # List Clusters in given Datacenter
        avail_clusters = []
        if datacenter is None:
            return avail_clusters
        clusters = datacenter.hostFolder.childEntity
        avail_clusters.extend([clusters[i].name for i in range(0, len(clusters)) if not isinstance(clusters[i], vim.Folder)])
        return avail_clusters

    def get_cluster(self, dc, c_name):
        if dc is None:
            return None
        if c_name is None:
            return None
        folder = dc.hostFolder
        if folder is not None and isinstance(folder, vim.Folder):
            for clust in folder.childEntity:
                if clust.name == c_name:
                    return clust

    def list_hosts(self, cluster):
        avail_hosts = []
        if cluster.host is not None:
            avail_hosts = [host.name for host in cluster.host]
        return avail_hosts

    def get_host(self, dc, c_name,h_name):
        if dc is None:
            return None
        if c_name is None:
            return None
        if h_name is None:
            return None
        folder = dc.hostFolder
        if folder is not None and isinstance(folder, vim.Folder):
            for clust in folder.childEntity:
                if clust.name == c_name:
                    for host in clust.host:
                        if host.name == h_name:
                            return host

    def list_vms(self, host):
        avail_vms = []
        if host.vm is not None:
            avail_vms = [vm.name for vm in host.vm]
        return avail_vms

    def disconnect_vc(self):
        connect.Disconnect(self.si)
        print '\nConnection Revoked'

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--host', help='IP of Vcenter', required=True)
    parser.add_argument('-u','--username', help='Username of Vcenter', required=True)
    parser.add_argument('-p','--password', help='Password of Vcenter', required=True)
    parser.add_argument('-o','--port', help='Port number of Vcenter', required=True)
    parser.add_argument('-i', '--interval', help='Interval to sleep in minutes', required=True)
    parser.add_argument('-t', '--tag', help='Tag for the run', required=True)
    args = parser.parse_args()

    # Connect to the VCenter Server.
    serv_details = {'host':args.host, 'user':args.username, 'passwd':args.password, 'port':args.port}

    while(1):
        stop = check_for_stop()
        if(stop=="false"):

            vc_obj = VCenterServerMonitor(serv_details)
            vc_obj.connect_vc()
            print "Results Calcaulation started.."
            vc_dict = {}
            # Perform verious monitoring operations
            dc_dict=[]
            all_dcs = vc_obj.list_datacenters()
            for x_dc in all_dcs:
                dc = {}
                dc['Name']=x_dc
                cluster_dict=[]
                dc_obj = vc_obj.get_datacenter(x_dc)
                all_clusters = vc_obj.list_clusters(dc_obj)
                for x_cluster in all_clusters:
                    cluster = {}
                    cluster['Name']=x_cluster
                    cluster_dict.append(cluster)
                    clust_obj = vc_obj.get_cluster(dc_obj, x_cluster)
                    all_hosts = vc_obj.list_hosts(clust_obj)
                    host_dict = []
                    for x_host in all_hosts:
                        host = {}
                        host['Name']=x_host
                        host_dict.append(host)
                        host_obj = vc_obj.get_host(dc_obj, x_cluster,x_host)
                        all_vms = vc_obj.list_vms(host_obj)
                        vm_dict = []
                        for x_vm in all_vms:
                            vm = {}
                            vm['Name'] = x_vm
                            vm_dict.append(vm)
                            host['VMs'] = vm_dict
                            cluster['Hosts'] = host_dict
                dc['Clusters'] = cluster_dict
                dc_dict.append(dc)
            vc_dict["Datacenters"] = dc_dict
            print "Completed.."
            #print json.dumps(vc_dict)
            url = "http://localhost:9200/vcenter/topology"
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(vc_dict),headers=headers)
            print "Results sent to elasticsearch."
            vc_obj.disconnect_vc()
        print "Sleep for interval of "+str(int(args.interval))+" minute(s)."
        time.sleep(int(args.interval)*60)

    vc_obj.disconnect_vc()
    return 0

if __name__ == "__main__":
    main()

