#   _     __   _______     _____ _                 _ 
#  | |    \ \ / /  __ \   / ____| |               | |
#  | |     \ V /| |  | | | |    | | ___  _   _  __| |
#  | |      > < | |  | | | |    | |/ _ \| | | |/ _` |
#  | |____ / . \| |__| | | |____| | (_) | |_| | (_| |
#  |______/_/ \_\_____/   \_____|_|\___/ \__,_|\__,_|
#                                                    

# REQUIREMENTS
#
# apt install python-configparser
#

# parse /etc/ansible/host file and get lxd_hosts
function lxd_hosts_get {
python - <<END
import configparser
config = configparser.ConfigParser(allow_no_value=True)
config.read('/etc/ansible/hosts')

for server in config['lxd_hosts']: print(server.split('.')[0])
END
}

# get list of servers
SERVERS=$(lxd_hosts_get)

# interate through list
for host in ${SERVERS}; do
 	echo "//////////////////////////////////////////////////////////////////////////"
 	echo $host

	# lxd list server to get containers
 	lxc list $host:
done
