#!/usr/bin/python
from __future__ import with_statement
import inspect, os, shutil
import subprocess
import datetime
import socket
import string
import sys
import logging
import logging.handlers
from tendo import singleton
import argparse

#def main():
#    # check if command exists
#    response = shell_exec('ls')

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-x",
    "--host",
    help = "Specify the host you wish to backup",
    required = True,
    type = str
  )
  return parser.parse_args()

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

# run a command
def shell_exec(command):
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        if errors:
                return False
        return output
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            # handle file not found error.
            return False
        else:
            return False

# rotate backups
def rotate_backup(host):

    retention_amount = 31
    path = {}
    path['base'] = '/vault/{folder}'
    path['arg'] = path['base'] + '/{host}/daily/{iteration}'

    output('[ {host} ]'.format(**{'host':host}))

    host_folder = {
        'backup': path['arg'].format(**{
        'folder':'backup',
            'host': host,
            'iteration':'00'
        }),
        'rotate': path['arg'].format(**{
            'folder':'backup',
            'host': host,
            'iteration':'00'
        }),
        'expired': path['arg'].format(**{
            'folder':'backup',
            'host': host,
            'iteration':str(retention_amount).rjust(2, '0')
        })        
    }

    # if not a folder or symlink skip / do not rotate
    if not os.path.isdir(host_folder['backup']):
        output(' - Skip missing ' + host_folder['backup'])
        return

    # delete the oldest folder to make room for new folder
    if os.path.isdir(host_folder['expired']):
        output(' - Remove folder ' + host_folder['expired'], False)
        try:
            shell_exec('rm -r ' + host_folder['expired'])
            status('PASS')
        except:
            status('FAIL')

    # rotate 03 to 04, 02 to 03, 01 to 02, etc.
    for i in range(retention_amount-1, -1, -1):
        folder_0 = path['arg'].format(**{
            'folder':'backup',
            'host': host,
            'iteration': str(i).rjust(2, '0')
        })
        folder_1 = path['arg'].format(**{
            'folder':'backup',
            'host': host,
            'iteration': str(i + 1).rjust(2, '0')
        })

        try:
            if os.path.exists(folder_0) and not os.path.exists(folder_1):     
                output(' - Move ' + folder_0 + ' ' + folder_1, False)
                cmd = 'mv ' + folder_0 + ' ' + folder_1

                shell_exec(cmd)
                status('PASS')

                # if moving 00 to 01 make copy of 01 back to 00 for quicker backups
                if i == 0:
                    output(' - Copy ' + folder_1 + ' ' + folder_0, False)
                    cmd = 'rsync -aAX --progress --delete --stats --hard-links ' + folder_1 + '/ ' + folder_0;
                    shell_exec(cmd)
                    status('PASS')
        except:
            status('FAIL')
            pass



if __name__ == "__main__":
	# only allow one instance at a time
	me = singleton.SingleInstance()

	global pending_notification
	global backup_missed
	global print_cache
	global log_runtime
        global args

	print_cache = ''
	pending_notification = False
	backups_missed = []

        # set args
        args = get_args()

	# create logging 
	log_runtime = create_logger()
        rotate_backup(args.host)
