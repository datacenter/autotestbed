import os
import requests
import json
import time


def get_nxapi_template():
    d = {
        "jsonrpc": "2.0",
        "method": "",
        "params": {
            "cmd": "",
            "version": 1
        },
        "id": 1
    }
    return d


def run_switch_cli(switch,command, method='cli'):
    url = 'http://'+switch["ip"]+'/ins'
    myheaders = {'content-type': 'application/json-rpc'}
    payload = get_nxapi_template()
    payload['method'] = method
    payload['params']['cmd']  = command
    time_out = 5
    response = requests.post(url, data=json.dumps(payload),
			     headers=myheaders,
			     auth=(switch["user"], switch["pwd"]),
			     timeout=time_out).json()
    return response


def get_all_switches():
    switches = [{"ip":"10.23.248.90","user":"admin","pwd":"cisco123"}, {"ip":"10.23.248.40","user":"admin","pwd":"cisco123"}]
    #switches = [{"ip":"172.25.187.219","user":"admin","pwd":"cisco123"}, {"ip":"172.25.187.220","user":"admin","pwd":"cisco123"}]
    #switches = [{"ip":"172.31.217.172","user":"admin","pwd":"cisco123"}, {"ip":"172.31.217.177","user":"admin","pwd":"C!sc0123"}]
    return switches
