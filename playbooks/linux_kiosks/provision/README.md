Install Ubuntu 18.04 LTS server from a DVD.

	For networking DHCP is fine for now.
	Skip proxy address
	Do not change the mirror/repos-- leave it as the Ubuntu repository -- the script will handle that
	During the installation use the whole harddrive for the partition. 
	The user created should be called the "{{ ansible_user }}"
	Use the standard "{{ ansible_user }}" password for the user.
	Select no on import SSH identity
	Do not install any snaps

After the install, run ip addr and write down the IP address assigned and place that and the password in /etc/ansible/hosts file:

	[linux_provision_machine]
	172.16.1.237    ansible_become_pass="INSERT PASSWORD"

Then enable the user to SSH by editing /etc/ssh/sshd_config and adding the following lines:

	AllowUsers {{ ansible_user }}
	PasswordAuthentication yes 

Restart SSH

	service sshd restart

The server should be properly connected test out whether or not you can SSH into the server from Ansible

	ssh user@x.x.x.x

If that works you should be ready to run the this playbook to setup the machine (specify the Ansible Interpreter to avoid python 2.6 issues).

	ansible-playbook playbook.yaml -e 'ansible_python_interpreter=/usr/bin/python3'

The networking at this point may not work

	You may need to add a Wireless Nic, etc. lshw will help you get the interface name

		lshw | less

		Find "logic name:" of network device

	Find and replace eno1 and replace with name of nic card 

		vim /etc/netplan/50-cloud-init.yaml

	netplan generate
	netplan apply
	ping google.com

If the kiosk doesn't come up on reboot try moving the machine to where it will be deployed.
The network assigned must be enabled on the port in order for the kiosk to come up.
