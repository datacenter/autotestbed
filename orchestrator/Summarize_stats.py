import requests
import json
import argparse

def inventory_count():
    topology_json = {}
    url = "http://localhost:9200/vcenter/topology/_search"
    query = json.dumps({
                "query": {
                    "match_all": {}
                 },
                 "size": 1,
                 "sort": [
                         {"timestamp": {
                              "order": "desc"
                              }
                         }
                  ]
           })
    r = requests.get(url,data=query)
    r_json = json.loads(r.text)
    dcs = r_json['hits']['hits'][0]['_source']['Datacenters']
    clusters_len = 0
    hosts_len = 0
    vms_len = 0
    for dc in dcs:
        clusters = dc['Clusters']
        clusters_len = clusters_len + len(clusters)
        for clus in clusters:
            hosts = clus['Hosts']
            hosts_len = hosts_len + len(hosts)
            for host in hosts:
                vms_len = vms_len + len(host['VMs'])
    topology_json['Datacenters'] = (len(dcs))
    topology_json["Clusters"]= (clusters_len)
    topology_json["Hosts"] = (hosts_len)
    topology_json["VMs"] = (vms_len)

    url = "http://localhost:9200/vcenter/datastore/_search"
    query = json.dumps({
                "query": {
                    "match_all": {}
                 },
                 "size": 1,
                 "sort": [
                         {"timestamp": {
                              "order": "desc"
                              }
                         }
                  ]
           })
    r = requests.get(url,data=query)
    r_json = json.loads(r.text)
    topology_json["Datastores"] = (len(r_json['hits']['hits'][0]['_source']['Datastores']))
    print json.dumps(topology_json)

def summarize_datastores():
    url = "http://localhost:9200/vcenter/datastore/_search"
    query = json.dumps({
                "query": {
                    "match_all": {}
                 },
                 "size": 1,
                 "sort": [
                         {"timestamp": {
                              "order": "desc"
                              }
                         }
                  ]
           })
    r = requests.get(url,data=query)
    print r.text


def dynamicParams(vm,vm_temp,param,hits_length):
    vm[param+'_Avg'] = str(float(vm[param+'_Avg'])+(float(vm_temp[param])/hits_length))
    vm[param+'_Max'] = vm[param] if (float(vm[param]) >= float(vm_temp[param])) else vm_temp[param]
    vm[param+'_Min'] = vm[param] if (float(vm[param]) < float(vm_temp[param])) else vm_temp[param]


def summarize_hosts(starttime,endtime):
    url = "http://localhost:9200/vcenter/host/_search"
    query = json.dumps({
          "query":{
             "filtered":{
                "filter":{
                    "range":{"timestamp":{"gte":starttime, "lte":endtime}}
                 }
              }
           },
                 "sort": [
                         {"timestamp": {
                              "order": "desc"
                              }
                         }
                  ]

          })
    r = requests.get(url,data=query)
    r_json = json.loads(r.text)
    hits_length = len(r_json['hits']['hits'])
    vm_array = r_json['hits']['hits'][0]['_source']['Hosts']

    for vm in vm_array:
        vm['Mem_Active(kB)_Avg'] = str(float(vm['Mem_Active(kB)'])/hits_length)
        vm['Mem_Granted(kB)_Avg'] = str(float(vm['Mem_Granted(kB)'])/hits_length)
        vm['Mem_Balloon(kB)_Avg'] = str(float(vm['Mem_Balloon(kB)'])/hits_length)
        vm['Mem_Consumed(kB)_Avg'] = str(float(vm['Mem_Consumed(kB)'])/hits_length)
        vm['Mem_Swap_Used(kB)_Avg'] = str(float(vm['Mem_Swap_Used(kB)'])/hits_length)
        vm['Mem_Shared_Common(kB)_Avg'] = str(float(vm['Mem_Shared_Common(kB)'])/hits_length)
        vm['CPU_Usage(%)_Avg'] = str(float(vm['CPU_Usage(%)'])/hits_length)
        vm['Data_Receive_Rate(kBps)_Avg'] = str(float(vm['Data_Receive_Rate(kBps)'])/hits_length)
        vm['Data_Transmit_Rate(kBps)_Avg'] = str(float(vm['Data_Transmit_Rate(kBps)'])/hits_length)
        vm['Data_Packets_Received_Avg'] = str(float(vm['Data_Packets_Received'])/hits_length)
        vm['Data_Packets_Transmitted_Avg'] = str(float(vm['Data_Packets_Transmitted'])/hits_length)
        vm['Disk_Read(kBps)_Avg'] = str(float(vm['Disk_Read(kBps)'])/hits_length)
        vm['Disk_Write(kBps)_Avg'] = str(float(vm['Disk_Write(kBps)'])/hits_length)

    for x in range(1,hits_length):
        hit = r_json['hits']['hits'][x]
        vm_temp_array = hit['_source']['Hosts']
        for vm_temp in vm_temp_array:
            for vm in vm_array:
                if(vm['Name']==vm_temp['Name']):
                    dynamicParams(vm,vm_temp,'Mem_Active(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Granted(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Balloon(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Consumed(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Swap_Used(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Shared_Common(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'CPU_Usage(%)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Receive_Rate(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Transmit_Rate(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Packets_Received',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Packets_Transmitted',hits_length)
                    dynamicParams(vm,vm_temp,'Disk_Read(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Disk_Write(kBps)',hits_length)
    print json.dumps(vm_array)

def summarize_vms(starttime,endtime):
    url = "http://localhost:9200/vcenter/vm/_search"
    query = json.dumps({ 
          "query":{ 
             "filtered":{ 
                "filter":{ 
                    "range":{"timestamp":{"gte":starttime, "lte":endtime}} 
                 }
	      }
	   },
                 "sort": [
                         {"timestamp": {
                              "order": "desc"
                              }
                         }
                  ]

	  })
    r = requests.get(url,data=query)
    r_json = json.loads(r.text)
    hits_length = len(r_json['hits']['hits'])
    vm_array = r_json['hits']['hits'][0]['_source']['VMs']
   
    for vm in vm_array:
        vm['Mem_Active(kB)_Avg'] = str(float(vm['Mem_Active(kB)'])/hits_length)
        vm['Mem_Granted(kB)_Avg'] = str(float(vm['Mem_Granted(kB)'])/hits_length)
        vm['Mem_Balloon(kB)_Avg'] = str(float(vm['Mem_Balloon(kB)'])/hits_length)
        vm['Mem_Consumed(kB)_Avg'] = str(float(vm['Mem_Consumed(kB)'])/hits_length)
        vm['CPU_Usage(%)_Avg'] = str(float(vm['CPU_Usage(%)'])/hits_length)
        vm['Data_Receive_Rate(kBps)_Avg'] = str(float(vm['Data_Receive_Rate(kBps)'])/hits_length)
        vm['Data_Transmit_Rate(kBps)_Avg'] = str(float(vm['Data_Transmit_Rate(kBps)'])/hits_length)
        vm['Data_Packets_Received_Avg'] = str(float(vm['Data_Packets_Received'])/hits_length)
        vm['Data_Packets_Transmitted_Avg'] = str(float(vm['Data_Packets_Transmitted'])/hits_length)
        vm['Disk_Read(kBps)_Avg'] = str(float(vm['Disk_Read(kBps)'])/hits_length)
        vm['Disk_Write(kBps)_Avg'] = str(float(vm['Disk_Write(kBps)'])/hits_length)
        vm['Storage_Space_Used(GB)_Avg'] = str(float(vm['Storage_Space_Used(GB)'])/hits_length)


    for x in range(1,hits_length):
        hit = r_json['hits']['hits'][x]
        vm_temp_array = hit['_source']['VMs']
        for vm_temp in vm_temp_array:
            for vm in vm_array:
                if(vm['Name']==vm_temp['Name']):
                    dynamicParams(vm,vm_temp,'Mem_Active(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Granted(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Balloon(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'Mem_Consumed(kB)',hits_length)
                    dynamicParams(vm,vm_temp,'CPU_Usage(%)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Receive_Rate(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Transmit_Rate(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Packets_Received',hits_length)
                    dynamicParams(vm,vm_temp,'Data_Packets_Transmitted',hits_length)
                    dynamicParams(vm,vm_temp,'Disk_Read(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Disk_Write(kBps)',hits_length)
                    dynamicParams(vm,vm_temp,'Storage_Space_Used(GB)',hits_length)

    print json.dumps(vm_array)


def main():
    #summarize_datastores()
    #inventory_count()

    parser = argparse.ArgumentParser()
    parser.add_argument('-st', '--starttime', help='Start time of interval to monitor in the format yyyy-mm-ddThh:mm:ss Example: -st 2016-05-06T11:30:00', required=True)
    parser.add_argument('-et', '--endtime', help='End time of interval to monitor in the format yyyy-mm-ddThh:mm:ss Example: -et 2016-05-06T11:45:00', required=True)
    args = parser.parse_args()
    
    #summarize_vms(args.starttime,args.endtime)
    summarize_hosts(args.starttime,args.endtime)

if __name__ == "__main__":
    main()
    
