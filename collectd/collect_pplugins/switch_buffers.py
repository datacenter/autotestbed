import os
import requests
import json
import time
import collectd
from switch_common import *
from logger import *

 
def get_buffers_statistics(switch, logger):
    try:
        response = run_switch_cli(switch, "show hostname") 
        if response['result'] == None:
            collectd.info('NXAPI Empty Response')
            return
        hostname = response['result']['body']['hostname']
        response = run_switch_cli(switch, "show hardware internal buffer info pkt-stats") 
        if response['result'] == None:
            collectd.info('NXAPI Empty Response')
            return
        else:
            slots = response['result']['body']['TABLE_module']['ROW_module']
            if type(slots) is not list:
                slots = [slots] 
            for slot in slots:
                instances = slot['TABLE_instance']['ROW_instance']
                if type(instances) is not list:
                    instances = [instances]
                for instance in instances:
                    instance['type'] = 'switch'
                    instance['plugin'] = 'buffer'
                    instance['subtype'] = hostname 
                    instance['slot'] = 'slot '+ slot['module_number']
                    instance['instance'] = instance['instance']
                    logger.info('switch_buffers', extra=instance)
    except Exception as e:
       print str(e)
       return


def collectd_buffers():
    logger = get_logstash_logger() 
    switches = get_all_switches()
    for switch in switches:
        get_buffers_statistics(switch, logger)


collectd.register_read(collectd_buffers)
