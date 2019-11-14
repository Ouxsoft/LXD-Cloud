Check to make sure your host machine is has RAID

Install Ubuntu 18.04 LTS server from a DVD.

	During the installation use the whole harddrive for the partition. LXD storage pools do not need to be separated.
	For networking DHCP is fine for now.
	The user selected should be called the standard SSH user.
	Use the SSH password for the user.
	Do not change the repos -- leave it as the Ubuntu repository -- the script will handle that


After the install, run ifconfig and write down the IP address assigned and place that and the password in /etc/ansible/hosts file:

	[linux_provision_machine]
	172.16.1.237    ansible_become_pass="INSERT PASSWORD"

Then enable the user to SSH by editing /etc/ssh/sshd_config

	AllowUsers [INSERT SSH USER]
	PasswordAuthentication yes 

Restart SSH

	service sshd restart


The server should be properly connected in the server room and on the correct network. Test out whether or not you can SSH into the server from ansible

	ssh user@172.16.1.237

If that works you should be ready to run the this playbook to setup the machine.

If test it out by moving a sample container to the machine and seeing if there is an issue with it. 

	In the past we haved issues with the VLANs configured on the server switch this might be worth looking into whether the correct ports are tagged.

Set the default storage pool on the host (this should be added to playbook):

	lxc profile device add default root disk path=/ pool=default

Add the host to ansible server (password in /etc/ansible/host_vars/server)

	lxc remote add server server.example.com
