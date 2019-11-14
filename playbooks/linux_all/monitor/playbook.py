#!/usr/bin/python
from __future__ import with_statement
from optparse import OptionParser
import inspect, os, shutil
import subprocess
import datetime
import socket
import smtplib
import string
import MySQLdb
from email.mime.text import MIMEText
import sys

def main():
	# define variables
	lxd_host = str(socket.gethostname())
	threshold = 0.9
	parser = OptionParser()
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="Print only container information related to problems")
        parser.add_option("--host", action="store", dest="host", default="", type="string", help="Database host")
        parser.add_option("--user", action="store", dest="user", default="", type="string", help="Database user")
        parser.add_option("--database", action="store", dest="database", default="", type="string", help="Database name")
        parser.add_option("--password", action="store", dest="password", default="", type="string", help="Database password")

	(options, args) = parser.parse_args()
	
	if(options.verbose):
		print 'LXD HOST :: ' + lxd_host

	# check release
	release_raw = shell_exec("cat /etc/issue");
	print release_raw

	if(("Ubuntu 18" in release_raw) or ("Ubuntu 17" in release_raw) or ("Ubuntu 16" in release_raw)):
		options.vmstat = True
		lxc_path = "/var/lib/lxd/containers"
	elif(("Ubuntu 14" in release_raw) or ("Ubuntu 12" in release_raw)):
		options.vmstat = False
		lxc_path = "/var/lib/lxc" 
	else:
		print "unsupported release"
	        return

	stats = stats_get("vmstat -s -SMB",options)


	# Connect to Codd for storage
        # TODO: get from pass / do not hard code
        db = MySQLdb.connect(host=options.host, user=options.user,passwd=options.password,db=options.database)
	cursor = db.cursor()
	
	# insert into history
	try:
		cursor.execute("INSERT INTO `history` (`container`, `usage`, `max_held`, `limit`, `rss`, `cache`, swap) VALUES (%s, %s, %s, %s, %s, %s, %s)",[lxd_host, stats['usage'], stats['max_held'], stats['limit'], stats['rss'], stats['cache'], stats['swap']])
		db.commit()
	except MySQLdb.Error, e:
		try:
			print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
		except IndexError:
			print "MySQL Error: %s" % str(e)	
	
	# Fetch last two rows and compare rss to threshold of limit and if over threshold
	# to previous rss and if different send email
	cursor.execute("SELECT `container`, `rss`, `limit` FROM `history` WHERE `container` = %s ORDER BY `timestamp` DESC LIMIT 2", [lxd_host])
	rows = cursor.fetchall()
	if(len(rows)>0) and (int(rows[0][1]/rows[0][2]) > threshold) and (rows[0][1] > rows[1][1]):                            
		print ' *** Host Exceeded 90% *** '
	if(rows[0][1]/rows[0][2] > threshold and rows[0][1] > rows[1][1]):				
		print ' *** Host Exceeded 90% *** '

	# Remove all associated containers and re-add below
	try:
		cursor.execute("DELETE FROM `organization` WHERE host = %s", [lxd_host])
		db.commit()
	except MySQLdb.Error, e:
		try:
			print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
		except IndexError:
			print "MySQL Error: %s" % str(e)


	# Loop over containers
	for lxc in next(os.walk(lxc_path))[1]:		
		# get each containers memory usuage 
		cgroup_path = '/sys/fs/cgroup/memory/lxc/' + lxc + '/'
		
		if(os.path.isfile(cgroup_path + 'memory.usage_in_bytes')):

			if options.verbose:
				print 'LXC CONTAINER :: ' + lxc
				
			if options.vmstat:
				stats = stats_get("lxc exec " + lxc + " -- bash -c 'vmstat -s -SMB'", options)
				# TODO: finalize variables
				stats['limit'] = stats['M total memory']
				stats['usage'] = stats['M used memory']
				stats['rss'] = stats['M used memory']
				stats['cache'] = stats['M swap cache']
				stats['swap'] = stats['M used swap']
				stats['max_held'] = int(shell_exec('cat ' + cgroup_path + 'memory.max_usage_in_bytes'))/1024/1024
			else:
				stats['limit'] = str(int(shell_exec('cat ' + cgroup_path + 'memory.limit_in_bytes'))*0.00000095367432)
				stats['usage'] = str(int(shell_exec('cat ' + cgroup_path + 'memory.usage_in_bytes'))/1024/1024)
				stats['rss'] = str(int(shell_exec("grep '^rss ' " + cgroup_path + 'memory.stat').split(' ')[1])/1024/1024)
				stats['cache'] = str(int(shell_exec("grep '^cache ' " + cgroup_path + 'memory.stat').split(' ')[1])/1024/1024)
				stats['swap'] = str(int(shell_exec("grep '^swap ' " + cgroup_path + 'memory.stat').split(' ')[1])/1024/1024)
				stats['max_held'] = str(int(shell_exec('cat ' + cgroup_path + 'memory.max_usage_in_bytes'))/1024/1024)
				
			try:
				if(int(int(stats['rss'])/int(stats['limit'])) > threshold):
					print("- WARNING: Exceeded 90 percent Threshold. \n-- RSS (%s) / LIMIT (%s) = %s percent" % (stats['rss'], stats['limit'], str(int(stats['rss']) / int(stats['limit']))))
			except:
				pass
			
			try:
				cursor.execute("INSERT INTO `history` (`container`, `usage`, `max_held`, `limit`, `rss`, `cache`, `swap`) values (%s, %s, %s, %s, %s, %s, %s)",[lxc, stats['usage'], stats['max_held'], stats['limit'], stats['rss'], stats['cache'], stats['swap']])
				cursor.execute("INSERT INTO `organization` (`host`, `container`) VALUES (%s, %s)", [lxd_host, lxc])
				db.commit()
			except MySQLdb.Error, e:
				try:
					print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
				except IndexError:
					print "MySQL Error: %s" % str(e)
			
			# Fetch last two rows and compare max_held to threshold of limit and if over threshold
			# to previous max_held and if different send email
			cursor.execute("SELECT `container`, `rss`, `limit` FROM `history` WHERE `container` = %s ORDER BY `timestamp` DESC LIMIT 2", [lxc])
			rows = cursor.fetchall()
			if(rows[0][1]/rows[0][2] > threshold and rows[0][1] > rows[1][1]):				
				print message
	cursor.close()			
			
			
# build a dictionary of vmstats
def stats_get(command,options):
	'''
	Resident set size (RSS)
	The portion of memory occupied by a process that is held in main memory (RAM).
	The rest of the occupied memory exists in the swap space or file system, either because some parts of the occupied memory were paged out, or because some parts of the executable were never loaded.
	Apparently done away with in free -m display in 16.04 where as it was in 14.04
	the Mem used(kb_main_used) field value is now calculated like this:
	used = total - free - cached - buffer
	Previously, it used to be:
	used = total - free
	Actual formula in 16.0x:
	cache = mb_main_free + buffers (mb_main_buffers) + cached (mb_main_cached)
	https://askubuntu.com/questions/770108/what-do-the-changes-in-free-output-from-14-04-to-16-04-mean/770125
	'''
	
	dictionary = {}
    
	if options.vmstat == True:
		for line in shell_exec(command).split('\n'):
			digits = ''
			for char in line.split():
				if char.isdigit():
					digits += char
			key = line.replace(digits, '', 1).strip()
			try:
				dictionary[key] = int(digits)
			except:
				pass
		dictionary['rss'] = str(dictionary['M free memory'] + dictionary['M buffer memory']  + dictionary['M swap cache'])
		dictionary['cache'] = str(dictionary['M swap cache'])
		dictionary['swap'] = str(dictionary['M used swap'])
		dictionary['usage'] = str(dictionary['M free memory'] + dictionary['M buffer memory'] + dictionary['M swap cache'])
		dictionary['max_held'] = str(0)
		dictionary['limit'] = str(dictionary['M used memory'])
	else:
		dictionary['rss'] = str(int(shell_exec("free -m | grep '^-/+ buffers/cache:'").split()[2]))
		dictionary['cache'] = str(int(shell_exec("free -m | grep '^Mem:'").split()[6]))
		dictionary['swap'] = str(int(shell_exec("free -m | grep '^Swap:'").split()[2]))
		dictionary['usage'] = str(int(shell_exec("free -m | grep '^-/+ buffers/cache:'").split()[2]))
		dictionary['max_held'] = str(0)
		dictionary['limit'] = str(int(shell_exec("free -m | grep '^Mem:'").split()[1]))

	if(options.verbose):
		print '- Active:  ' + string.rjust(dictionary['rss'], 10) + ' MB' 
		print '- Cache:   ' + string.rjust(dictionary['cache'],10) + ' MB'
		print '- Swap:    ' + string.rjust(dictionary['swap'],10) + ' MB'
		print '- Max Held:' + string.rjust(dictionary['max_held'],10) + ' MB'
		print '- Limit:   ' + string.rjust(dictionary['limit'],10)  + ' MB'

	# return onl items of concern
	return dictionary

# A convenience method that takes a string or array in the formate expected by subprocess.popen
# and returns the stdout, displaying any stderr if one occurs 
def shell_exec(command):
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, errors = proc.communicate()
	if errors:
		raise Exception("ERROR: " + errors)
	return output

# run things
if __name__ == "__main__":
	main()
