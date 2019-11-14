LXD containers may result in an ERROR state for a multitude of reasons, which may result in the service going down. 

This playbook chceks each LXD server and attempts to restore any containers in an ERROR state.

The script will not restore a container when the LXD monitor is hung or when ERROR state results from a kernel issue.

If that happens use the following command to troubleshoot further and restart the machine if necessary:

	lxc monitor --pretty --type logging

You may be able to restart the container, but that's what this script tries to do. 
Chances are if this script does not work you'll need to restart the host

	lxc restart <container>



