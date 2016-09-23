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
        import ssl
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

'''
Build query helps in calling the performance manager and get all the values over that interval
'''
def BuildQuery(content, vchtime, counterId, instance, vm, interval):
    perfManager = content.perfManager
    metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance=instance)
    startTime = vchtime - timedelta(minutes=(interval + 1))
    endTime = vchtime - timedelta(minutes=1)
    query = vim.PerformanceManager.QuerySpec(intervalId=20, entity=vm, metricId=[metricId], startTime=startTime,
                                             endTime=endTime)
    perfResults = perfManager.QueryPerf(querySpec=[query])
    #if perfResults:
    return perfResults
    #else:
    #    print('Performance results empty.  TIP: Check time drift on source and vCenter server')

'''
This function is used to get the counterId of any parameter which performance manager can recognise
'''
def StatCheck(perf_dict, counter_name):
    counter_key = perf_dict[counter_name]
    return counter_key

def main():

    interval=20
    statInt = interval * 3
    
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
            Get all the virtual machines of vcenter
            '''
            content = si.RetrieveContent()
            perf_dict = {}
            perfList = content.perfManager.perfCounter
            for counter in perfList:
                counter_full = "{}.{}.{}".format(counter.groupInfo.key,counter.nameInfo.key,counter.rollupType)
                perf_dict[counter_full] = counter.key
               
            viewType = [vim.VirtualMachine]
            props = ['name','runtime.powerState', 'datastore']
            specType = vim.VirtualMachine
            objView = content.viewManager.CreateContainerView(content.rootFolder,viewType,True)  
            tSpec = vim.PropertyCollector.TraversalSpec(name='tSpecName', path='view', skip=False, type=vim.view.ContainerView)    
            pSpec = vim.PropertyCollector.PropertySpec(all=False, pathSet=props,type=specType)   
            oSpec = vim.PropertyCollector.ObjectSpec(obj=objView,selectSet=[tSpec],skip=False)   
            pfSpec = vim.PropertyCollector.FilterSpec(objectSet=[oSpec], propSet=[pSpec], reportMissingObjectsInResults=False)   
            vm_properties = content.propertyCollector.RetrieveProperties(specSet=[pfSpec])  
            objView.Destroy()
            vchtime = si.CurrentTime()
            count = 0
            print "Results Calculation started.."
            vms_json = []
            for vm_property in vm_properties:
                property_dic = {}
                for prop in vm_property.propSet:
                    property_dic[prop.name] = prop.val
                vm = vm_property.obj
                vm_mor = vm._moId
                vm_dict ={}
        
                '''
                If a virtual machine is powered on Collect the dynamic parameters
                '''
                if "poweredOn" in vm.runtime.powerState:
                    count= count + 1
                    vm_dict["Name"]=vm.name

                    '''
                    CPU Stats
                    '''
                    cpuAllocation = vm.config.cpuAllocation
                    cpuShares = cpuAllocation.shares.shares
                    numvcpus = 0
                    if (cpuAllocation.shares.level == "normal"):
                        numvcpus = cpuShares/1000
                    if (cpuAllocation.shares.level == "high"):
                        numvcpus = cpuShares/2000
                    if (cpuAllocation.shares.level == "low"):
                        numvcpus = cpuShares/500
                    vm_dict["Number_of_vCPUs"]=str(numvcpus)
          
                    statCpuUsage = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'cpu.usage.average')), "", vm, interval)
                    cpuUsage = ((float(sum(statCpuUsage[0].value[0].value)) / statInt) / 100)
                    vm_dict['CPU_Usage(%)']=str(cpuUsage)
 
                    '''
                    Memory Stats
                    '''
                    memAllocation = vm.config.memoryAllocation
                    memShares = memAllocation.shares.shares
                    meminMB = 0
                    if (memAllocation.shares.level == "normal"):
                        meminMB = memShares/10
                    if (memAllocation.shares.level == "high"):
                        meminMB = memShares/20
                    if (memAllocation.shares.level == "low"):
                        meminMB = memShares/5
                    vm_dict["Memory(MB)"]=str(meminMB)

                    statMemActive = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'mem.active.average')), "", vm, interval)
                    memActive = ((float(sum(statMemActive[0].value[0].value)) / statInt))
                    vm_dict["Mem_Active(kB)"]=str(memActive)

                    statMemGranted = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'mem.granted.average')), "", vm, interval)
                    memGranted = ((float(sum(statMemGranted[0].value[0].value)) / statInt))
                    vm_dict["Mem_Granted(kB)"]=str(memGranted)

                    statMemConsumed = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'mem.consumed.average')), "", vm, interval)
                    memConsumed = ((float(sum(statMemConsumed[0].value[0].value)) / statInt))
                    vm_dict["Mem_Consumed(kB)"]=str(memConsumed)

                    statMemBalloon = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'mem.vmmemctl.average')), "", vm, interval)
                    memBalloon = ((float(sum(statMemBalloon[0].value[0].value)) / statInt))
                    vm_dict["Mem_Balloon(kB)"]=str(memBalloon)

                    '''
                    Network Stats
                    '''
                    statNetTransmitted = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'net.transmitted.average')), "", vm, interval)
                    netTransmitted = ((float(sum(statNetTransmitted[0].value[0].value)) / statInt))
                    vm_dict["Data_Transmit_Rate(kBps)"]=str(netTransmitted)

                    statNetReceived = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'net.received.average')), "", vm, interval)
                    netReceived = ((float(sum(statNetReceived[0].value[0].value)) / statInt))
                    vm_dict["Data_Receive_Rate(kBps)"]=str(netReceived)

                    statNetPcktRx = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'net.packetsRx.summation')), "", vm, interval)
                    netPcktRx = ((float(sum(statNetPcktRx[0].value[0].value))))
                    vm_dict["Data_Packets_Received"]=str(netPcktRx)

                    statNetPcktTx = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'net.packetsTx.summation')), "", vm, interval)
                    netPcktTx = ((float(sum(statNetPcktTx[0].value[0].value))))
                    vm_dict["Data_Packets_Transmitted"]=str(netPcktTx)

                    '''
                    Disk Stats
                    '''
                    statDiskRead = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'disk.read.average')), "", vm, interval)
                    if not statDiskRead:
                        diskRead = 0
                    else:
                        diskRead = ((float(sum(statDiskRead[0].value[0].value)) / statInt))
                    vm_dict["Disk_Read(kBps)"]=str(diskRead)

                    statDiskWrite = BuildQuery(content, vchtime, (StatCheck(perf_dict, 'disk.write.average')), "", vm, interval)
                    if not statDiskWrite:
                        diskWrite = 0
                    else:
                        diskWrite = ((float(sum(statDiskWrite[0].value[0].value)) / statInt))
                    vm_dict["Disk_Write(kBps)"]=str(diskWrite)

                    perDatastoreUsage = vm.storage.perDatastoreUsage
                    used = 0
                    provisioned = 0
                    unshared = 0
                    for perUsage in perDatastoreUsage:
                        used = perUsage.committed + used
                        provisioned = (perUsage.committed) + (perUsage.uncommitted) + provisioned
                        unshared = perUsage.unshared + unshared
                    vm_dict["Storage_Space_Used(GB)"]=str(float(used)/1024/1024/1024)
                    vm_dict["Storage_Space_Provisioned(GB)"]=str(float(provisioned)/1024/1024/1024)
                    vm_dict["Storage_Space_Unshared(GB)"]=str(float(unshared)/1024/1024/1024)
                    '''
                    Virtual Disks
                    '''
                    vm_hardware = vm.config.hardware
                    disk_list = []
                    for each_vm_hardware in vm_hardware.device:
                        vdisk_dict = {}
                        if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
                            vdisk_dict["Name"]=str(each_vm_hardware.deviceInfo.label)
                            vdisk_dict["Size(GB)"]=str(each_vm_hardware.capacityInKB/1024/1024)
                            vdisk_dict["Thin"]=str(each_vm_hardware.backing.thinProvisioned)
                            vdisk_dict["Datastore_Path"]=str(each_vm_hardware.backing.fileName)
                            disk_list.append(vdisk_dict)
            

                    vm_dict["Virtual_Disks"]=disk_list
                    vms_json.append(vm_dict)

            payload = {}
            ts = time.time()
            payload['timestamp'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')
            payload['Tag'] = args.tag

            payload['VMs'] = vms_json
            print "Completed.."
            #print json.dumps(payload)
            url = "http://localhost:9200/vcenter/vm"
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(payload),headers=headers)
            print "Results sent to elasticsearch.."
            connect.Disconnect(si)
            print "Connection revoked."
        print "Sleep for interval of "+ str(int(args.interval)) +" minute(s)"
        time.sleep(int(args.interval)*60)
        
    connect.Disconnect(si)
    print '\nConnection Revoked.'

if __name__ == "__main__":
    main()

