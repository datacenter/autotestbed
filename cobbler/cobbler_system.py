#!/usr/bin/python
import os
import re
import time
import json
import logging
import xmlrpclib
import argparse
from configobj import ConfigObj
import subprocess
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
frmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(frmt)
logger.addHandler(fh)
logger.info("\n")


class system:
    def __init__(self):
        try:
            self.config = ConfigObj('config.cfg')
            cobbler_url = "http://"+self.config['server']['ip']+"/cobbler_api"
            self.server = xmlrpclib.Server(cobbler_url)
            cobbler_ip = self.config['server']['ip']
            cobbler_user_name = self.config['server']['user_name']
            cobbler_password = self.config['server']['password']
            print "Checking cobbler ip %s reachability..." % (cobbler_ip)
            logger.info("Checking cobbler %s ip reachability" % (cobbler_ip))
            response2 = os.system("ping -c 5 " + cobbler_ip + ">> /dev/null")
            if response2:
                print 'Cobbler IP %s unavailable' % (cobbler_ip)
                logger.error('Cobbler IP %s unavailable' % (cobbler_ip))
                raise Exception('Cobbler IP-%s unavailable' % (cobbler_ip))
            self.token = self.server.login(cobbler_user_name, cobbler_password)
        except Exception as e:
            print e
            logger.error(e)
            raise Exception(e)

    # To validate config file data
    def validateData(self, system_type):
        try:
            for nodes in self.config['system'][system_type]:
                print "Validating node-%s ..." % (nodes)
                logger.info("Validating node %s " % (nodes))
                cimc_ip = self.config['system'][system_type][nodes]['CIMC_ip']
                cimc_user = self.config['system'][system_type][nodes]['CIMC_user']
                cimc_password = self.config['system'][system_type][nodes]['CIMC_password']
                cimc_mac = self.config['system'][system_type][nodes]['macaddress']
                kvm_ip = self.config['system'][system_type][nodes]['kvm_ip']
                print "Checking CIMC ip %s reachability..." % (cimc_ip)
                logger.info("Checking CIMC ip %s reachability" % (cimc_ip))
                response = os.system("ping -c 2 " + cimc_ip + ">> /dev/null")
                if response:
                    print 'CIMC IP-%s unreachable' % (cimc_ip)
                    logger.error('CIMC IP-%s unreachable' % (cimc_ip))
                    raise Exception('CIMC IP-%s unreachable' % (cimc_ip))
                print "Checking CIMC mac address %s..." % (cimc_mac)
                logger.info("Checking CIMC mac address %s" % (cimc_mac))
                a = subprocess.Popen(['./macList.sh', str(cimc_user), str(cimc_ip), str(cimc_password)], stdout=subprocess.PIPE)
                out, err = a.communicate()
                flag = 0
                #  print out
                for i in out.split('\n'):
                    #   print i
                    if re.search(cimc_mac, i):
                        flag = 1
                if flag == 0:
                    print 'CIMC mac-%s not found' % (cimc_mac)
                    logger.error('CIMC mac-%s not found' % (cimc_mac))
                    raise Exception('CIMC mac-%s not found' % (cimc_mac))
                print "Checking for KVM ip %s availability..." % (kvm_ip)
                logger.info("Checking for KVM ip %s availability" % (kvm_ip))
                dhcp_file = open('/var/lib/dhcp/dhcpd.leases', 'r')
                ip = 0
                for line in dhcp_file:
                    if re.search(kvm_ip, line):
                            ip = 1
                response1 = os.system("ping -c 2 " + kvm_ip + ">> /dev/null")
                if response1 == 0: #or ip == 1:
                    print 'KVM IP-%s unavailable to assign' % (kvm_ip)
                    logger.error('KVM IP-%s unavailable to assign' % (kvm_ip))
                    raise Exception('KVM IP-%s unavailable' % (kvm_ip))
        except Exception as e:
            raise Exception(e)

    # To create cobbler systems using config file data
    def createSystem(self):
        try:
            print "Updating seedfile..."
            logger.info("Updating seedfile")
            seed_file = open(self.config['files']['seedfile_path'], 'r')
            lines = seed_file.readlines()
            seed_file.close()
            new_seed_file = open(self.config['files']['seedfile_path'], 'w')
            for line in lines:
                if not re.search('/target/root/.ssh', line):
                    new_seed_file.write(line)
            with open(self.config['files']['sshkey_path'], 'r') as myfile:
                key = myfile.read().replace('\n', '')
            cmd1 = ">> /target/root/.ssh/authorized_keys; chmod 600 /target/root/.ssh/authorized_keys;"
            cmd2 = " mkdir /target/root/.ssh/node; chmod 777 /target/root/.ssh/node;  echo $system_name>> /target/root/.ssh/node/$system_name;"
            string = "d-i     preseed/late_command string mkdir /target/root/.ssh; chmod 700 /target/root/.ssh; echo " + '"' + key + '"' + cmd1 + cmd2
            new_seed_file.write(string)
            kernal_string = "netcfg/link_detection_timeout=20 netcfg/dhcp_timeout=120 netcfg/choose_interface=auto"
            profile_id = self.server.new_profile(self.token)
            self.server.modify_profile(profile_id, 'name',   self.config['profile']['name'], self.token)
            self.server.modify_profile(profile_id, 'distro',   self.config['profile']['distro'], self.token)
            self.server.modify_profile(profile_id, 'kickstart', self.config['files']['seedfile_path'], self.token)
            self.server.modify_profile(profile_id, 'kopts',  kernal_string, self.token)
            self.server.save_profile(profile_id, self.token)
            for nodes in self.config['system']['create_system']:
                print "creating system %s ..." % (nodes)
                logger.info("creating system %s" % (nodes))
                system_id = self.server.new_system(self.token)
                system_name = self.config['system']['create_system'][nodes]['name']
                if system_name in self.server.find_system():
                    self.server.remove_system(system_name, self.token)
                self.server.modify_system(system_id, "name", system_name, self.token)
                host_name = self.config['system']['create_system'][nodes]['hostname']
                self.server.modify_system(system_id, "hostname", host_name, self.token)
                self.server.modify_system(system_id, 'modify_interface', {
                "macaddress-eth0": self.config['system']['create_system'][nodes]['macaddress'],
                "ipaddress-eth0": self.config['system']['create_system'][nodes]['kvm_ip'],
                "static-eth0": True,
                "netmask-eth0": self.config['system']['create_system'][nodes]['kvm_subnet'],
                "gateway-eth0": self.config['system']['create_system'][nodes]['kvm_gateway'],
                }, self.token)
                profile_name = self.config['system']['create_system'][nodes]['profile']
                self.server.modify_system(system_id, "profile", profile_name, self.token)
                self.server.save_system(system_id, self.token)
                self.server.sync(self.token)
                print "Updating json file..."
                logger.info("Updating json file")
                file1 = open('output.json', 'w')
                file1.close()
                if os.stat('output.json').st_size:
                    json_data = open("output.json")
                    data = json.load(json_data)
                    json_data.close()
                    json_data = open('output.json', 'w')
                    data.update(self.config['system']['create_system'])
                else:
                    data = self.config['system']['create_system']
                    json_data = open('output.json', 'w')
                    json.dump(data, json_data, indent=4)
                json_data.close()
        except Exception as e:
            raise Exception(e)

    # To modify the cobbler systems using config file data
    def modifySystem(self, list):
        try:
            print "modifying system attributes"
            logger.info("modifying system attributes")
            system_list = self.server.find_system()
            for nodes in self.config['system']['modify_system']:
                if 'all' not in list:
                    if self.config['system']['modify_system'][nodes]['name'] not in list:
                        print "System not yet created"
                        continue
                print "modifying system %s attributes" % (nodes)
                logger.info("modifying system %s attributes" % (nodes))
                system = self.config['system']['modify_system'][nodes]['name']
                if system not in system_list:
                    print "No system with name-%s" % (system)
                    logger.warn("No system with name-%s" % (system))
                    continue
                self.server.remove_system(system, self.token)
                system_id = self.server.new_system(self.token)
                system_name = self.config['system']['modify_system'][nodes]['name']
                if system_name in self.server.find_system():
                    self.server.remove_system(system_name, self.token)
                self.server.modify_system(system_id, "name", system_name, self.token)
                host_name = self.config['system']['modify_system'][nodes]['hostname']
                self.server.modify_system(system_id, "hostname", host_name, self.token)
                self.server.modify_system(system_id, 'modify_interface', {
                "macaddress-eth0": self.config['system']['modify_system'][nodes]['macaddress'],
                "ipaddress-eth0": self.config['system']['modify_system'][nodes]['kvm_ip'],
                "static-eth0": True,
                "netmask-eth0": self.config['system']['modify_system'][nodes]['kvm_subnet'],
                "gateway-eth0": self.config['system']['modify_system'][nodes]['kvm_gateway'],
                }, self.token)
                profile_name = self.config['system']['modify_system'][nodes]['profile']
                self.server.modify_system(system_id, "profile", profile_name, self.token)
                self.server.save_system(system_id, self.token)
                print "Updating json file"
                logger.info("Updating json file")
                json_data = open("output.json")
                data = json.load(json_data)
                json_data.close()
                for i in data:
                    if data[i]['name'] == self.config['system']['modify_system'][nodes]['name']:
                        data[i] = self.config['system']['modify_system'][nodes]
                json_data = open('output.json', 'w')
                json.dump(data, json_data, indent=4)
                json_data.close()
        except Exception as e:
            raise Exception(e)

    #To delete cobbler systems
    def deleteSystem(self, list):
        try:
            for system in list:
                if system in self.server.find_system():
                    print "Deleting system %s" % (system)
                    logger.info("Deleting system %s" % (system))
                    self.server.remove_system(system, self.token)
                    print "Updating json file"
                    logger.info("Updating json file")
                    json_data = open("output.json")
                    data = json.load(json_data)
                    json_data.close()
                    flag = ""
                    for node in data:
                        if data[node]['name'] == system:
                            flag = node
                    del data[node]
                    json_data = open('output.json', 'w')
                    json.dump(data, json_data, indent=4)
                    json_data.close()
                else:
                    print "unable to delete the system %s" % (system)
                    logger.warn("unable to delete the system %s" % (system))
        except Exception as e:
            raise Exception(e)

    def addNetBootAndPowerReset(self, list):
        try:
            json_data = open('output.json')
            data = json.load(json_data)
            json_data.close()
            ip_list = []
            system_list = []
            for node in data:
                if list[0] == 'all' or data[node]['name'] in list:
                    print "refreshing node %s" % (node)
                    print data[node]['name']
                    logger.info("refreshing node %s" % (node))
                    cimc_ip = data[node]['CIMC_ip']
                    cimc_user = data[node]['CIMC_user']
                    cimc_password = data[node]['CIMC_password']
                    print "Changing bootorder to PXE"
                    logger.info("Changing bootorder to PXE")
                    ip_list.append(data[node]['kvm_ip'])
                    system_list.append(data[node]['name'])
                    subprocess.call(['./boot_order.sh', str(cimc_user), str(cimc_ip), str(cimc_password), str('pxe')])
                    print "power reset"
                    logger.info("power reset")
                    time.sleep(5)
                    power_cycle = "ipmitool -I lanplus -H "+cimc_ip+" -U "+cimc_user+" -P "+cimc_password+" chassis power reset"
                    os.system(power_cycle)
                    time.sleep(200)
                    print "Changing bootorder to DISK"
                    logger.info("Changing bootorder to DISK")
                    subprocess.call(['./boot_order.sh', str(cimc_user), str(cimc_ip), str(cimc_password), str('disk')])
            if not 'all' in list:
                for node in list:
                    for ele in data:
                        if node not in data[ele]['name']:
                            print "System %s not yet created" % (node)
                            logger.warn("System %s not yet created" % (node))
            os.system("rm /home/cisco/cobbler_result/* 2>/dev/null")
            time.sleep(450)
            end_time = time.time() + 60 * 2
            while time.time() < end_time:
                for host in ip_list:
                    string = "scp -o 'StrictHostKeyChecking no' "+host+":/root/.ssh/node/* /home/cisco/cobbler_result > /dev/null 2>&1"
                    os.system(string)
            booted_system_list = os.listdir("/home/cisco/cobbler_result/")
            result_file = open("node_details", 'w')
            result_file.write("System_name		Status\n")
            for node in system_list:
                if node in booted_system_list:
                    result_file.write("%s              Success/Installed\n" % (node))
                    print "OS installation on %s successfull " % (node)
                    logger.info("OS installation on %s successfull " % (node))
                else:
                    result_file.write("%s              Failed/Uninstalled\n" % (node))
                    print "OS installation failed on %s. Please check manually" % (node)
                    logger.info("OS installation failed on %s. Please check manually" % (node))
        except Exception as e:
            raise Exception(e)

    def installationStatus(self):
        try:
            status = open("node_details", 'r')
            for line in status:
                print line
                logger.info(line)
        except Exception as e:
            raise Exception(e)


def main():
    try:
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-add_system", help="To add cobbler system", action="store_true")
        group.add_argument("-modify_system", nargs='+', help="To modify cobbler system ex: all or node_name")
        group.add_argument("-boot_system", nargs='+', help="To boot added system ex: all or node name")
        group.add_argument("-delete_system", nargs='+', help="To delete cobbler systems ex: node names")
        group.add_argument("-get_status", help="To get cobbler system installation details", action="store_true")
        args = parser.parse_args()

        if args.add_system:
            try:
                obj = system()
                obj.validateData('create_system')
                obj.createSystem()
            except Exception as e:
                print e

        if args.modify_system:
            try:
                system_list = args.modify_system
                obj = system()
                obj.validateData('modify_system')
                obj.modifySystem(list(system_list))
            except Exception as e:
                print e

        if args.boot_system:
            try:
                system_list = args.boot_system
                obj = system()
                obj.addNetBootAndPowerReset(list(system_list))
            except Exception as e:
                print e

        if args.delete_system:
            try:
                system_list = args.delete_system
                obj = system()
                obj.deleteSystem(list(system_list))
            except Exception as e:
                print e

        if args.get_status:
            try:
                obj = system()
                obj.installationStatus()
            except Exception as e:
                print e

    except Exception as e:
        print e


if __name__ == '__main__':
    main()
