This playbook automatically makes entries for servers in nagios and restarts the service

The hosts file contains all the hosts and host groups that are made in nagios.

The services.cfg file contains a list of services that are attached.

To run the playbook you'll need the following to dig the server's IP

pip install dnspython
