import logging
import logstash


def get_logstash_logger():
    if get_logstash_logger.logger is None: 
	    get_logstash_logger.logger = logging.getLogger('python-logstash-logger')
	    get_logstash_logger.logger.setLevel(logging.INFO)
	    get_logstash_logger.logger.addHandler(logstash.TCPLogstashHandler('localhost', 5000, version=1))
	    #logger.addHandler(logstash.LogstashHandler('localhost', 5959, version=1))
    return get_logstash_logger.logger


get_logstash_logger.logger = None


