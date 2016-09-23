master_nodes = ['192.168.101.7', '192.168.101.10'] # primary and failover rm  node
zk_nodes = ['192.168.101.7', '192.168.101.9', '192.168.101.10'] # 
rm_host = 'root@' + master_nodes[0] ### Primary RM

logstash_host = 'localhost'
log_stash_file_name  = '/home/monitoring/tempserver.json'

hadoop_uname = 'mapr'


apps_url = 'http://%s:8088/ws/v1/cluster/apps'
jobs_url = 'http://%s:8088/proxy/%s/ws/v1/mapreduce/jobs/'
counter_url = 'http://%s:8088/proxy/%s/ws/v1/mapreduce/jobs/%s/counters'
cluster_metrics_url = 'http://%s:8088/ws/v1/cluster/metrics'
cluster_info_url = 'http://%s:8088/ws/v1/cluster/info'
cluster_nodes_url = 'http://%s:8088/ws/v1/cluster/nodes'
mapr_nodes_url = 'https://%s:8443/rest/node/list?columns=service,health,configuredservice'

#hdfs_cmd = 'hdfs dfsadmin -report'
#yarn_node_cmd = 'yarn node -list'
mapr_nodes_list_cmd = 'sudo -u %s maprcli node list -columns service,health,healthDesc,configuredservice -json' % (hadoop_uname)
cluster_capacity_cmd = 'hadoop fs -df -h'
list_jobs_cmd = 'mapred job -list' #
job_status_cmd = 'mapred job -status %s'
zk_status_cmd = 'service mapr-zookeeper status'

app_key_ar = ['id', 'name', 'finishedTime', 'startedTime', 'elapsedTime', 'state', 'progress', 'finalStatus', 'runningContainers', 'allocatedVCores', 'clusterId', 'user', 'memorySeconds', 'vcoreSeconds', 'allocatedMB', 'applicationType']
job_key_ar = ['id', 'elapsedTime', 'mapsPending', 'state', 'mapsCompleted', 'startTime', 'reducesPending', 'reduceProgress', 'finishTime', 'mapProgress', 'reducesCompleted', 'mapsTotal', 'reducesTotal', 'mapsRunning', 'reducesRunning', 'failedReduceAttempts', 'failedMapAttempts', 'killedMapAttempts', 'killedReduceAttempts', 'mapsTotal', 'reducesTotal', 'mapProgress']
cluster_key_ar = ['id', 'haState', 'hadoopVersion', 'startedOn', 'state']
