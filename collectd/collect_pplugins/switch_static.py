import os
import requests
import json
import time
import collectd
from switch_common import *
from logger import *

    
def get_static_information(switch, logger):
    sw_details ={}
    sw_details['type'] = 'switch'
    sw_details['plugin'] = 'static'
    sw_details['instance'] = 'NA'
    try:
        response = run_switch_cli(switch, "show hardware")
        if response['result'] == None:
            colectd.info('NXAPI Empty Response')
            return
        else:
            sw_details['manufacturer'] = response['result']['body']['manufacturer']
            sw_details['chassis_id'] = response['result']['body']['chassis_id']
            sw_details['subtype'] = response['result']['body']['host_name']
            sw_details['memory'] = response['result']['body']['memory']
            sw_details['mem_type'] = response['result']['body']['mem_type']
            sw_details['cpu_name'] = response['result']['body']['cpu_name']
            sw_details['bios_ver_str'] = response['result']['body']['bios_ver_str']

        response = run_switch_cli(switch, "show vlan")
        if response['result'] == None:
            colectd.info('NXAPI Empty Response')
            return
        else:
            vlans = response['result']['body']['TABLE_vlanbrief']['ROW_vlanbrief']
            if type(vlans) is not list:
                vlans = [vlans]
            sw_details['vlans'] = []
            for vlan in vlans:
                vlan_id = vlan['vlanshowbr-vlanid-utf']
                vlan_interfaces = vlan['vlanshowplist-ifidx'] if vlan.has_key('vlanshowplist-ifidx') else None
                sw_details['vlans'].append({'vlan_id': vlan_id, 'vlan_interfaces': vlan_interfaces})
        logger.info('switch_static', extra=sw_details)
    except Exception as e:
       print str(e)
       return

def collectd_static():
    logger = get_logstash_logger()
    switches = get_all_switches()
    for switch in switches:
        get_static_information(switch, logger)


collectd.register_read(collectd_static)
