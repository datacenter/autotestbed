import collectd

from utility import *

from globals import *

import subprocess
import shlex

import json

import logger

def get_clusterInfo_stats_data(resource_master):
    cluster_info_dict = get_http_response(cluster_info_url%(resource_master))
    if not cluster_info_dict: 
        return {}
    res_dict = cluster_info_dict['clusterInfo']
    if res_dict.get('startedOn', ''):
        res_dict['startedOn'] = get_formated_date(res_dict['startedOn'])
    new_res_dict = {}
    for kval in cluster_key_ar:
        if res_dict.get(kval, ''):
            new_res_dict['cluster_'+ kval] = res_dict[kval]
    return new_res_dict

def get_clusterMetrics_stats_data(resource_master):
    cluster_metrics_info_dict = get_http_response(cluster_metrics_url%(resource_master))
    res_dict = cluster_metrics_info_dict['clusterMetrics']
    new_res_dict = {}
    for kval, vval in res_dict.items():
        new_res_dict['yarn_'+ kval] = res_dict[kval]
    return new_res_dict

def get_clusterNodes_stats_data(resource_master):
    cluster_node_info_dict = get_http_response(cluster_nodes_url%(resource_master))
    nodes_info = cluster_node_info_dict.get('nodes', {}).get('node', [])
    new_res_dict = {}
    for node_info in nodes_info:
        new_res_dict[node_info['nodeHostName']] = node_info
    return new_res_dict

def get_yarn_node_details(stdoutsp_ar):
    split_ar = [x.strip() for x in  stdoutsp_ar if x.strip()]
    header_line_ar = []
    res_dict = {'total_yarn_node':{}, 'nodes_info':[]}
    for i, each_line in enumerate(split_ar):
        tmp_dict = {}
        if 'Total Nodes' in each_line:
            tmp_dict['Total_Yarn_Nodes'] = each_line.split(':')[1].strip()
            res_dict['total_yarn_node'] = tmp_dict
            tmp_dict = {}
        elif 'Node-Id' in each_line:
            header_line_ar = each_line.split('\t')
            header_line_ar = [x.strip() for x in header_line_ar]
            header_line_ar = map(lambda x:'_'.join(x.split('-')), header_line_ar)
        elif header_line_ar:
            node_detail_ar = each_line.split('\t')
            node_detail_ar = [x.strip() for x in node_detail_ar]
            for hval, nval in zip(header_line_ar, node_detail_ar):
                tmp_dict[hval] = nval
            if tmp_dict:
                res_dict['nodes_info'].append(tmp_dict)
    return res_dict

def get_data_node_details(stdoutsp_ar):
    split_ar = [x.strip() for x in  stdoutsp_ar]
    tmp_dict = {}
    res_dict = {'cluster_data': {}, 'nodes_data':{}}
    cnt = 0
    for each_line in split_ar:
        if not each_line.strip() and tmp_dict:
            if cnt < 1:
                res_dict['cluster_data'] = tmp_dict
            else:
                res_dict['nodes_data'][tmp_dict['Hostname']] = tmp_dict
            tmp_dict = {}
            cnt += 1
        if each_line.strip():
            if 'Live datanodes' in each_line:
                t_val =  each_line.strip('Live datanodes').strip('(').strip('):')
                res_dict['Live_datanodes'] = int(t_val.strip())
            elif ':' in each_line:
                each_line = each_line.strip()
                sp_ar = each_line.strip().split(':')
                t_val = ':'.join(sp_ar[1:]).strip().rstrip('%')
                for m_val in [' GB)', ' MB)', ' B)']:
                    if m_val in str(t_val):
                        t_val = get_int_val(str(t_val).split('(')[1].split(m_val)[0].strip())
                t_key = '_'.join(sp_ar[0].strip().split()).replace('(', '').replace(')', '')
                if t_key[-1] == '%':
                    t_key = t_key[:-1] + '_percent'
                    t_val = get_float_val(t_val)
                if t_key in ['DFS_Remaining', 'DFS_Used', 'Configured_Capacity', 'Non_DFS_Used', 'Configured_Capacity', 'Present_Capacity']:
                    t_val = get_float_val(t_val)
                if t_key in ['Under_replicated_blocks', 'Blocks_with_corrupt_replicas', 'Missing_blocks', 'Missing_blocks_with_replication_factor_1', 'Xceivers']:
                    t_val = get_int_val(t_val)
                tmp_dict[t_key] = t_val
    new_dict = {}
    for kval, vval in  res_dict['cluster_data'].items():
        new_dict['cluster_'+kval] = vval
    res_dict['cluster_data'] = new_dict
    return res_dict

def get_float_val(val):
    try:
        val = float(val)
    except:
        pass
    return val
     
def get_int_val(val):
    try:
        val = int(val)
    except:
        pass
    return val
     
def get_all_static_stats(data=None):
    static_dict = {}  
  
    zoo_keeper_state_cnt = 0
    for zk_node in zk_nodes:
        zk_status_cmd_sp = shlex.split(zk_status_cmd)
        p_obj = subprocess.Popen(['ssh', 'root@'+zk_node] + zk_status_cmd_sp, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdinp , stdoutp = p_obj.communicate()
        if 'zookeeper running as process' in stdinp:
            zoo_keeper_state_cnt += 1

    static_dict['zoo_keeper_status'] = 'Partially Healthy'
    if zoo_keeper_state_cnt == len(zk_nodes):
        static_dict['zoo_keeper_status'] = 'Healthy'
    elif not zoo_keeper_state_cnt:
        static_dict['zoo_keeper_status'] = 'Unhealthy'

    static_dict['stat_type'] = 'hadoop'
    static_dict['plugin'] = 'hadoop_static_data'

    data_sent_flg = 0
    for resource_master in master_nodes:
        cluster_res_info_dict = get_clusterInfo_stats_data(resource_master)
        if not cluster_res_info_dict:continue
        static_dict.update(cluster_res_info_dict)

        static_dict['resource_master_host_name'] = resource_master

        #cluster_metrics_res_dict = get_clusterMetrics_stats_data(resource_master)
        #static_dict.update(cluster_metrics_res_dict)

        cluster_capcity_cmd_sp = shlex.split(cluster_capacity_cmd)
        p_obj = subprocess.Popen(['ssh', 'root@'+resource_master] + cluster_capcity_cmd_sp, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdinp , stdoutp = p_obj.communicate()
        cluster_capacity_res = stdinp.split('\n')
        if len(cluster_capacity_res)>1 and 'Filesystem' in cluster_capacity_res[0]:
             cluster_detail_ar = cluster_capacity_res[1].split()
             res_dict = {'cluster_filesystem': cluster_detail_ar[0],
                         'cluster_size':float(cluster_detail_ar[1]),
                         'cluster_used_size':float(cluster_detail_ar[3]),
                         'cluster_available_Size':float(cluster_detail_ar[5]),
                         'cluster_use_Percentage':float(cluster_detail_ar[7].strip('%s')),
                        }
             static_dict.update(res_dict)

        mapr_nodes_list_cmd_sp = shlex.split(mapr_nodes_list_cmd)
        p_obj = subprocess.Popen(['ssh', 'root@'+resource_master] + mapr_nodes_list_cmd_sp, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdinp , stdoutp = p_obj.communicate()
        ddict = {}
        try:
            ddict = json.loads(stdinp)
        except:
            pass

        error_nodes = []
        if ddict:
            total_cluster_nodes  = ddict.get('total', 0)
            static_dict.update({'total_cluster_nodes': total_cluster_nodes})
            service_data_dict = {}
            conf_service_data_dict = {}
            for node_dict in ddict.get('data', []):
                configuredservice_ar = node_dict.get('configuredservice', '').split(',')
                service_ar = node_dict.get('service', '').split(',')
                hostname = node_dict.get('hostname', '')
                health = node_dict.get('health', -1)
                if health >= 4:
                    error_nodes.append(hostname)
                
                for service_name in service_ar:
                    if not service_data_dict.get(service_name, []):
                        service_data_dict[service_name] = []
                    service_data_dict[service_name].append(hostname)
                for service_name in configuredservice_ar:
                    if not conf_service_data_dict.get(service_name, []):
                        conf_service_data_dict[service_name] = []
                    conf_service_data_dict[service_name].append(hostname)
            #cluster_nodes_res_dict = get_clusterNodes_stats_data(resource_master)
            static_dict.update({'error_nodes_list': ', '.join(error_nodes), 'error_nodes': len(error_nodes)})

            #YARN  NODES
            yarn_node_details = {'yarn_nodes_list': service_data_dict.get('nodemanager', []), 'Total_Yarn_Nodes':len(service_data_dict.get('nodemanager', []))}
            static_dict.update(yarn_node_details)
            conf_yarn_node_details = {'Configured_yarn_nodes_list': ', '.join(conf_service_data_dict.get('nodemanager', [])), 'Configured_Total_Yarn_Nodes':len(conf_service_data_dict.get('nodemanager', []))}
            static_dict.update(conf_yarn_node_details)
      
            #DATA  NODES
            data_node_details = {'data_nodes_list': service_data_dict.get('nfs', []), 'Total_Data_Nodes':len(service_data_dict.get('nfs', []))}
            static_dict.update(data_node_details)
            conf_data_node_details = {'Configured_data_nodes_list': ', '.join(conf_service_data_dict.get('nfs', [])), 'Configured_Total_Data_Nodes':len(conf_service_data_dict.get('nfs', []))}
            static_dict.update(conf_data_node_details)

            #RM NODES
            rm_node_details = {'resource_manager_list':service_data_dict.get('resourcemanager', []), 'Total_RM_Nodes':len(service_data_dict.get('resourcemanager', []))}
            static_dict.update(rm_node_details)
            conf_rm_node_details = {'Configured_resource_manager_list':', '.join(conf_service_data_dict.get('resourcemanager', [])), 'Configured_Total_RM_Nodes':len(conf_service_data_dict.get('resourcemanager', []))}
            static_dict.update(conf_rm_node_details)

            node_data_dict = {'Yarn_Node':service_data_dict.get('nodemanager', []), 'Data_Node':service_data_dict.get('nfs', []), 'RM_Node':service_data_dict.get('resourcemanager', [])}
            topology_ar = get_topology_details(node_data_dict)
            static_dict.update({'topology': topology_ar})
            pl_logger = logger.get_logstash_logger()
            pl_logger.info('Static Data', extra=static_dict)
            data_sent_flg = 1
            break

    if not data_sent_flg:
        pl_logger = logger.get_logstash_logger()
        pl_logger.info('Static Data', extra=static_dict)

def get_topology_details(node_data_dict):
    node_type_dict = {}
    for node_type, node_list in node_data_dict.items():
        for node_name in node_list:
            if not node_type_dict.get(node_name, []):
                node_type_dict[node_name] = []
            node_type_dict[node_name].append(node_type)

    topology_ar = []
    for node_name, node_type_ar in node_type_dict.items():
        topology_ar.append((node_name, node_type_ar))
    return topology_ar

collectd.register_read(get_all_static_stats, interval=30)
