import os
import requests
import json
import time
import collectd
from switch_common import *
from logger import *

def get_buffer_details(switch):
    response = run_switch_cli(switch, "show interface hardware-mapping","cli_ascii")
    if response['result'] == None:
	collectd.info('NXAPI Empty Response')
	return
    interface_buffer_usage = {}
    mappings = response['result']['msg'].split('\n')[14:-5]
    response = run_switch_cli(switch, "show hardware internal buffer info pkt-stats peak") 
    if response['result'] == None:
	collectd.info('NXAPI Empty Response')
	return
    instances = response['result']['body']['TABLE_module']['ROW_module']['TABLE_instance']['ROW_instance']
    peak_buffer_usage = {}
    for instance in instances:
        peak_buffer_usage[instance['instance']]={value['oport']:value['count_0'] for value in instance['TABLE_peak']['ROW_peak'][1:]}
    #print peak_buffer_usage
    #collectd.info(str(peak_buffer_usage))
    for mapping in mappings:
        #print mapping
        t = mapping.split()
        print t
	#print peak_buffer_usage[t[8]][t[9]]
	try:
            interface_buffer_usage[t[0]] = peak_buffer_usage[t[8]][t[9]]
	except Exception as e:
	    pass
    return interface_buffer_usage
    


def get_interface_statistics(switch, logger):
    #active_interfaces = []
    try:
        response = run_switch_cli(switch, "show hostname") 
        if response['result'] == None:
            collectd.info('NXAPI Empty Response')
            return
        hostname = response['result']['body']['hostname']
	print "HostName : "+hostname
        response = run_switch_cli(switch, "show cdp neighbors") 
        if response['result'] == None:
            collectd.info('NXAPI Empty Response')
            return
        cdp_neighbors = response['result']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
        response = run_switch_cli(switch, "show interface") 
        if response['result'] == None:
            collectd.info('NXAPI Empty Response')
            return
        interfaces = response['result']['body']['TABLE_interface']['ROW_interface']
        interface_buffer_usage = get_buffer_details(switch) 
        for itf in interfaces:
            if any(itf['interface'].find(pattern) == 0 for pattern in ['Vlan','port-channel','mgmt']):
                continue
            interface = {}
	    try:
                for key in ['state','interface','eth_inbytes','eth_outbytes','eth_inpause','eth_outpause','eth_inerr','eth_outerr']:
                    interface[key] = itf[key]
	        for neighbor in cdp_neighbors:
                    if neighbor['intf_id'] == interface['interface']:
		        interface['cdp_device_id'] = neighbor['device_id'] 
		        interface['cdp_platform_id'] = neighbor['platform_id'] 
		        interface['cdp_port_id'] = neighbor['port_id'] 
                        break     
	        if 'cdp_device_id' not in interface.keys():
		    interface['cdp_device_id'] = 'None' 
		    interface['cdp_platform_id'] = 'None'
		    interface['cdp_port_id'] = 'None' 
                interface['buffer_util'] = interface_buffer_usage[interface['interface'].replace("ernet","")]
	        interface['instance'] = interface['interface']
            except Exception as e:
		pass
                #collectd.info('Key Not Found: '+str(e))
                #continue 
            interface['type'] = 'switch'
	    interface['plugin'] = 'interface'
	    interface['subtype'] = hostname
            logger.info('switch_interface', extra=interface)
    except Exception as e:
        print str(e)
        collectd.info('EXCEPTION : '+str(e))       
        return


def collectd_interfaces():
    logger = get_logstash_logger()
    switches = get_all_switches()
    for switch in switches:
        get_interface_statistics(switch, logger)

#collectd_interfaces()
collectd.register_read(collectd_interfaces)
