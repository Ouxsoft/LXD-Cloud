How to start a new container

	Step 1: Add DNS record.
		
		(done on DNS server)

	Step 2: Run the provision playbook

		ansible-playbook /etc/ansible/playbooks/linux/containers/provision/playbook.yaml

	Step 3: Configure server

		At the end of the previous step/playbook it will give you a command. Run this to then configure the server

		e.g.

			ansible-playbook /etc/ansible/playbooks/linux/containers/configure/playbook.yaml --extra-vars "container=sso.example.com"

	Step 3: Add host to approperiate host groups (it should already be there as a container)

		vim /etc/ansible/hosts 

	Step 4:

		Run Nagios playbook to add monitoring for container

	Step 5: 

		Add the password to your password manager and update it


If you're trying to recreate a server that has already been in ansible you'll need to do the following previously

	lxc stop foo:bar
	lxc delete foo:bar
	rm /etc/ansible/host_vars/bar.example.com 
	ssh-keygen -R bar.example.com
	ssh-keygen -R {INSERT IP ADDRESS}
