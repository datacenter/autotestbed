import collectd

from utility import *

from globals import *

import logger

def read_stats_data(data=None):
    new_dict = {}
    for resource_master in master_nodes:
        all_apps_data_dict = get_http_response(apps_url%(resource_master))
        if not all_apps_data_dict:continue
        all_apps = all_apps_data_dict.get('apps', {}).get('app', [])
        for app_data_dict in all_apps:
            if app_data_dict['state'] == 'RUNNING':
                for app_key in app_key_ar:
                    if app_key in ['progress']:
                        new_dict['application_'+app_key] = '%.*f' % (1, float(app_data_dict[app_key]))
                    elif app_key in ['elapsedTime']:
                        new_dict['application_'+app_key] = int(app_data_dict[app_key]) / 1000
                    else:
                        new_dict['application_'+app_key] = app_data_dict[app_key]
                new_dict['application_startedTime'] = get_formated_date(new_dict['application_startedTime'])
                application_finishedTime = new_dict['application_finishedTime']
                if int(application_finishedTime) != 0:
                    new_dict['application_finishedTime'] = get_formated_date(application_finishedTime)
                else:
                    new_dict['application_finishedTime'] = '0'

                jobs_data_dict = get_http_response(jobs_url%(resource_master , app_data_dict['id']))
                all_app_jobs = jobs_data_dict.get('jobs', {}).get('job', [])
                for job_data_dict in all_app_jobs:
                    counter_data_dict = get_http_response(counter_url%(resource_master, app_data_dict['id'], job_data_dict['id']))
                    if counter_data_dict:
                        counters_ar = counter_data_dict.get('jobCounters', {}).get('counterGroup', [])
                        for cddict in counters_ar:
                            for tcdict in cddict['counter']:
                                new_dict['job_counter_' + tcdict['name'] + '_totalCounterValue'] = tcdict['totalCounterValue']
                                new_dict['job_counter_' + tcdict['name'] + '_mapCounterValue'] = tcdict['mapCounterValue']
                                new_dict['job_counter_' + tcdict['name'] + '_reduceCounterValue'] = tcdict['reduceCounterValue']
                    for job_key in job_key_ar:
                        if job_key in ['mapProgress', 'reduceProgress']:
                            new_dict['job_'+job_key] = '%.*f' % (1, float(job_data_dict[job_key]))
                        elif job_key in ['elapsedTime']:
                            new_dict['job_'+job_key] = int(job_data_dict[job_key]) / 1000
                        else:
                            new_dict['job_'+job_key] = job_data_dict[job_key]
                        new_dict['JobTagID'] = new_dict['job_id']
                new_dict['job_startTime'] = get_formated_date(new_dict['job_startTime'])
                job_finishTime = new_dict['job_finishTime']
                if int(job_finishTime) != 0:
                    new_dict['job_finishTime'] = get_formated_date(job_finishTime)
                else:
                    new_dict['job_finishTime'] = '0'
                cluster_id = int(new_dict['application_id'].split('_')[1])
                new_dict['cluster_id'] = cluster_id
                new_dict['stat_type'] = 'hadoop'
                new_dict['plugin'] = 'hadoop_dynamic_data'
                break
            if new_dict:
                break
        if new_dict:
            break
    if new_dict:
        pl_logger = logger.get_logstash_logger() 
        pl_logger.info('RUNNING JOB', extra=new_dict)
    return
 
collectd.register_read(read_stats_data, interval=30)
