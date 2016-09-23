import collectd
import subprocess
#import logstash
import re
def read(data=None):
#    print "read"
    try:
        p = subprocess.Popen(["lsblk","-no", "KNAME,SIZE,TYPE,ROTA"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return (-1)
    lsblk, err = p.communicate()
    if err:
        return (-1)
    lsblk = re.split("\n", lsblk)
    index = 0
    num_lines = len(lsblk)
    disks = []
    while index < num_lines:
        line = lsblk[index]
        if line:
            parts = re.split(r'\s+', line.strip())
            name, size,type,rota = parts[:4]
            if type == "disk":
                disks.append(name)
        index = index + 1

    if not disks:
        return (-1) 
#    for name in disks:
#       print name

    f = open("/sys/block/sda/queue/hw_sector_size", "r")
    if f is None:
	return (-1)
    sector_size = int(f.readline())
#    print sector_size
    f.close()
    f = open('/proc/diskstats', 'r')
    if f is None:
        return (-1)

    flag_disk_found = 0
    read_sectors = 0
    write_sectors = 0
    for line in f.readlines():
	parts = line.split()
        disk_name = parts[2]
	if disk_name in disks:
#	    print disk_name
            if len(parts) == 7:       
		flag_disk_found = 1
	    	read_sectors = read_sectors + int(parts[4])
            	write_sectors = write_sectors + int( parts[6])
            elif len(parts) == 14:
		flag_disk_found = 1
	    	read_sectors = read_sectors + int(parts[5])
            	write_sectors = write_sectors + int( parts[9])

    total_read_bytes = read_sectors*sector_size 
    total_write_bytes = write_sectors*sector_size
#    print total_read_bytes 
#    print total_write_bytes 
    f.close()
    if flag_disk_found == 0:
        return (-1)

    metric = collectd.Values();
    metric.plugin = 'readdisk'
    metric.type = 'disk_octets'
    metric.type_instance = "all"
    metric.values = [total_read_bytes, total_write_bytes]
    metric.dispatch()
# collectd.info(name)
#read()
collectd.register_read(read, interval=30)
