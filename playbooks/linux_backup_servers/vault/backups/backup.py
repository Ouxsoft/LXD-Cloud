#!/usr/bin/python
from __future__ import with_statement
import inspect, os, shutil
import subprocess
import datetime
import time
from time import sleep
import socket
import string
import sys
import logging
import logging.handlers
from tendo import singleton
import argparse
import paramiko
import json

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-x",
    "--fqdn",
    help = "FQDN of the server",
    required = True,
    type = str
  )
  parser.add_argument(
    "-f",
    "--hostname",
    help = "Specify the hostname",
    required = True,
    type = str
  )
  return parser.parse_args()


# display time as HMS
def duration_format(sec_elapsed):
	h = int(sec_elapsed / (60 * 60))
	m = int((sec_elapsed % (60 * 60)) / 60)
	s = sec_elapsed % 60.
	return "{}:{:>02}:{:>05.2f}".format(h, m, s)


# log results
def create_logger():
	# create logger for "Sample App"
	log_runtime = logging.getLogger('automated_runtime')
	log_runtime.setLevel(logging.DEBUG)

	# create file handler which logs even debug messages
	fh = logging.FileHandler('results.log', mode='w')
	fh.setLevel(logging.DEBUG)

	# create formatter and add it to the handlers
	formatter = logging.Formatter('[%(asctime)s] %(message)s ',datefmt='%Y-%m-%d %H:%M:%S')
	fh.setFormatter(formatter)
	#ch.setFormatter(formatter)

	# add the handlers to the logger
	log_runtime.addHandler(fh)

	return log_runtime
#
#    db = MySQLdb.connect(
#      host = conf['logger']['mysql']['host'],
#      user = conf['logger']['mysql']['user'],
#      passwd = conf['logger']['mysql']['password'],
#      db = conf['logger']['mysql']['database']
#    )
#    cursor = db.cursor()
#    try:
#      if log_type == 'backup':
#        output('Log backup', False)
#        cursor.execute("INSERT INTO `backupschedule` (`host`, `start`, `end`, `startgroup`, `backupserver`) values (%s,%s,%s,%s,%s)", (
#          lxc_host['name'],
#          start_datetime,
#          end_datetime,
#          conf['runtime'],
#          conf['local_info']['hostname']))
#      elif log_type == 'rotate':
#        output('Log rotate',False)
#        cursor.execute("INSERT INTO `rotateschedule` (`host`, `start`, `end`, `startgroup`, `backupserver`) values (%s,%s,%s,%s,%s)", (
#          lxc_host['name'],
#          start_datetime,
#          end_datetime,
#          conf['runtime'],
#          conf['local_info']['hostname']))
#    db.commit()


# provide status output
def status(var):
    output('[' + var + ']',True,False)
    return

# provide output
def output(string, clear = True, timestamp = True):
    # global print_cache
    # global log_runtime    
    
    if string is None or string.isspace():
	return

    if(timestamp):
        print '[' +  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] ',

    if(clear):
	print string
    else:
	print string,
        
    log_runtime.log(logging.INFO, string)


# connect to lxc_host via SSH key
def ssh_connect(fqdn):
    global ssh
    global containerization

    output(' - Login ', False)
    try:
        # create paramiko ssh client
        ssh = paramiko.SSHClient()
        ssh._policy = paramiko.WarningPolicy()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # select key
        ssh_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/lxd_hosts')

	# automatically add remote host keys
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # create a log file for SSH because stdout may be large during rsync
	try:
            os.remove('transfer.log')
	except OSError:
	    pass
	os.mknod('transfer.log')
        paramiko.util.log_to_file('transfer.log')

        # try connecting
        ssh.connect(fqdn,username='root',pkey=ssh_key)

    except paramiko.SSHException:
        status('FAIL')
        return False

    # show user logged in as
    user = ssh_exec('whoami').strip()
    output(' as ' + user, False, False)
    status('PASS')
    return True

# ssh exec and output return
def ssh_exec(command):
	# check if still connected
	if ssh.get_transport().is_active() == False:
            output(' Disconnected cannot run command: ', False)
            status('FAIL')
            output(command, True)
            return False
            
	# check if active again as returning false positives
        try:
            transport = ssh.get_transport()
            transport.send_ignore()
        except EOFError, e:
            # connection is closed
            output(' Disconnected cannot run command: ', False)
            status('FAIL')
            output(command, True)
            return False

	# standard input - where process reads to get information from user
	# standard output - where process writes normal information to this file handle
	# standard error - where process writes error information
	stdin, stdout, stderr = ssh.exec_command(command)

	# wait until a response hasn't been seen for timeout period
	# incase command does not return EOF
	timeout = 30
	endtime = time.time() + timeout
	while not stdout.channel.eof_received:
		sleep(1)
		if time.time() > endtime:
			stdout.channel.close()
			break

	string = ''
	for line in stdout.readlines():
		string += line
	return string.strip()

# run a command
def shell_exec(command):
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        if errors:
                return False
        return output.strip()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            # handle file not found error.
            return False
        else:
            return False

# backup host
def backup_host(fqdn, hostname):
    global path
    global verbose

    output('[ {host} ]'.format(**{'host':fqdn}))

    try:
            # make backup folder for rsync if missing
            if not os.path.exists(path['backup']):
                output('Make ' + path['backup'],False)
                os.makedirs(path['backup'])
                if not os.path.exists(path['backup']):
                    status('FAIL')
                else:
                    status('PASS')

            output(' - Copy {host_address}:/ {host_dir}/'.format(**{
                'host_address' : fqdn,
                'host_dir' : path['backup']
                }), False)

            # rsync lxc host to backup host using inode / hard linking
            cmd = 'rsync -aAX --progress --delete --stats --link-dest={hard_link_dir} --exclude={exclude_paths} {host_address}:/ {host_dir}/'.format(**{
		    'hard_link_dir' : path['rotate'],
                    'exclude_paths' : ' --exclude='.join(path['exclude']),
                    'host_address' : fqdn,
                    'host_dir' : path['backup']
                    })

            if verbose:
                output(cmd)
                os.system(cmd)
            else:
                shell_exec(cmd)

            # touch host backup to indicate backup processed
            shell_exec('touch ' + path['backup'])

            status('N/A')
    except:
            status('FAIL')

# get array of containers on machine
def get_containers():
    global containerization

    try:
        if containerization == 'lxd':
            output('- Get LXD containers', False)
            raw = ssh_exec('lxc list -cn --format json') 
            containers = json.loads(raw)
            status('PASS')
        elif containerization == 'lxc':
            output('- Get LXC containers', False)
            containers = []
            raw = ssh_exec('ls /var/lib/lxc').split()
            for container in raw:
                state = ssh_exec('lxc-info -s -n ' + str(container)).split(":")[-1].strip()
                containers.append({'name':str(container),'status':str(state)})
            status('PASS')
        else:
            output('- No containers found', False)
            containers = []
            status('PASS')
    except:
        containers = []
        status('FAIL')

    return containers

# get containerization method of virtual machine
def containerization_get():
    output(' - Determine containerization ',False) 
    
    vm_type  = ssh_exec('if test -d /var/lib/lxd/containers; then echo \'lxd\'; elif test -d /var/lib/lxc/; then echo \'lxc\'; else echo \'none\'; fi;')

    if vm_type == 'lxd':
        output('(LXD found)', False, False)
    elif vm_type == 'lxc':
        output('(LXC found)', False, False)
    else:
        output('(none found)', False, False)
        vm_type = ''

    status('PASS')

    return vm_type

#un mount lxc_container
def lxc_rootfs_umount(container):
    rootfs = '/var/lib/lxc/' + container['name'] + '/rootfs'

    #f(not os.path.isdir(rootfs)):
    #   output('ERROR: rootfsfor ' + container['name'] + ' does not exist')
    #   return False

    try:
        ssh_exec('umount ' + rootfs)
    except Exception as error:
        output('ERROR: Failed to unmount lvm for ' + container['name'] + ', you may need to do this manually')
        output(error)
        return

    return True

# mount volume group
def lxc_rootfs_mount(container):
    rootfs = '/var/lib/lxc/' + container['name'] + '/rootfs'
    config = '/var/lib/lxc/' + container['name'] + '/config'

    if lxc_rootfs_umount(container) == False:
        return False

    config = ssh_exec('cat ' + config)

    for line in config.splitlines():
        if 'lxc.rootfs' in line:
            volume = line.split("=")[-1].strip()

    ssh_exec('mount ' + volume + ' ' + rootfs)

    return True

# backup a host container
def backup_host_container(fqdn, name, container):
    global path
    global verbose
    global containerization

    output('  - Process "' + container['name'] + '" ...')
    # find container's storage pool
    output('  - Find storage pool ',False)

    try:
        if containerization == 'lxd':
            # get the location of the contain's storage pool
            container_storage_pool_dir = ssh_exec('readlink -f /var/lib/lxd/containers/' + container['name'])
        elif containerization == 'lxc':
            container_storage_pool_dir = ssh_exec('readlink -f /var/lib/lxc/' + container['name'])
        else:
            output('- Skipping')
            return
        
        output(container_storage_pool_dir,False,False)
        status('PASS')
    except:
        status('FAIL')
        pass
 
    container_backup_dir = path['backup'] + container_storage_pool_dir
    container_rotate_dir = path['rotate'] + container_storage_pool_dir

    # make container folder on backup if does not exists
    if not os.path.exists(container_backup_dir):
        output('- Make ' + container_backup_dir,False)
        os.makedirs(container_backup_dir)
        status('PASS')
 
    # if container is running stop it unless it's ansible
    if container['status'].lower() == "Running".lower() and container['name'].lower() != 'ansible':
        output('  - Stop container', False)

        # start downtime timer
        start_timer = time.time()

        # issue different commands based on containerization method
        if containerization == 'lxd':
            # stop container only allow 30 seconds for stopdown to accomidate for hang
            ssh_exec('lxc stop --timeout 30 ' + container['name'])
            # after the up to 30 second wait issue a kill command to be sure its stopped
            ssh_exec('lxc stop --force ' + container['name'])
        
            # switch to pause if no database detected
        elif containerization == 'lxc':
            ssh_exec('lxc-freeze -n ' + container['name'])

        status('N/A')
       
    # mount rootfs if needed
    if containerization == 'lxc':
        lxc_rootfs_mount(container)

    try:
        output('  - Copy container (may take a while)... ',False)
        
        # backup the containers storage pool
        exclude_paths = ["/rootfs" + exclude for exclude in path['exclude']]

	# backup container
        cmd = 'rsync -aAX --progress --delete --stats --link-dest={hard_link_dir} --exclude={exclude_paths} {host_address}:{dir_from}/ {dir_to}'.format(
          exclude_paths = ' --exclude='.join(exclude_paths),
          host_address = fqdn,
	  hard_link_dir = container_rotate_dir,
          dir_from = container_storage_pool_dir,
          dir_to = container_backup_dir
        )
        if verbose:
            output(cmd)
            os.system(cmd)
        else:
            shell_exec(cmd)

        status('PASS')
    except:  
        output(command)                                                
        status('FAIL')
        
    # if container was running start it again unless it is ansible
    if container['status'].lower() ==  "Running".lower()  and container['name'].lower() != 'ansible':
        output('  - Restart container', False)

        # issue different commands depending on containerization method
        if containerization == 'lxd':
            ssh_exec('lxc start ' + container['name'])
        elif containerization == 'lxc':
            ssh_exec('lxc-unfreeze -n ' + container['name'])

        status('N/A')

        # output downtime
        end_timer = time.time()
        output('  - Restored after {} of downtime'.format(duration_format(end_timer - start_timer)))
   
    # umount rootfs if needed
    if containerization == 'lxc':
        lxc_rootfs_umount(container)  

if __name__ == "__main__":
	# only allow one instance at a time
	me = singleton.SingleInstance()

	global log_runtime
        global args
        global path
        global ssh
        global containers
        global verbose
        global containerization_method
        
        # debug turn on to see Rsync info
        verbose = False

        # get args passed
        args = get_args()

        path = {}
        path['base'] = '/vault/{folder}'
        path['arg'] = path['base'] + '/{host_folder}/daily/{iteration}'
        path['exclude'] = {
          "/var/spool/apt-mirror/*",
          #"/dev/*",
          "/proc/*",
          "/sys/*",
          "/tmp/*",
          "/run/*",
          "/mnt/*",
          "/media/*",
          "/lost+found",
          #"/var/lib/lxd/storage-pools/*/containers/",
          #"/var/lib/lxc/*",
          "/rucksack/*",
          "/vault/*",
          "/drobo/*",
          "/backup/*",
          "/disk/*",
          "/disks/*",
          "/rotate/*",
          "/root/vpn/*"
          }

        path['backup'] = path['arg'].format(**{
            'folder' : 'backup',
            'host_folder' : args.hostname,
            'iteration': '00'
	})

        path['rotate'] = path['arg'].format(**{
            'folder' : 'backup',
            'host_folder' : args.hostname,
            'iteration': '01'
	})


	# create logging 
	log_runtime = create_logger()

        # establish ssh connection to host
        ssh_connect(args.fqdn)

        # get containerization method and containers
        containerization = containerization_get()
        if containerization != '':
            containers = get_containers()

            if containers:
                # exclude containers from host backup
                for container in containers:
                    if containerization == 'lxd':
                        path['exclude'].add(str('/var/lib/lxd/storage-pools/*/containers/' + container['name'] + '/'))
                    elif containerization == 'lxc':
                        path['exclude'].add(str('/var/lib/lxc/' + container['name'] + '/'))
        else:
            containers = []    

        # backup hosts
        backup_host(args.fqdn, args.hostname)

        # backup container file system
        for container in containers:
            backup_host_container(args.fqdn, args.hostname, container)
