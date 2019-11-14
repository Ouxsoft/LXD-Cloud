# LXD Cloud

## About
LXD Cloud combines Ansible server automation with LXD's system container manager for lightweight server management.

Features include:
+ Automated host machine provisioning and configuration
+ Automated container provisioning and configuration
+ Automated host machine updates
+ Manually update all servers with oversight
+ Automated nagios intergration
+ Server per container backups with hardlink rotates (drastically reduce incremental backup downtime and size)
+ Automated KIOSK deployment

# Quickstart
Install Ansible

On Fedora, CentOS 8
> sudo dnf install ansible
(see Ansible docs for other distros)

> cd /etc/ansible

> git clone (this repository)

## System Configuration
Setup each of the following Ansible files. Reference Ansible documentation.

> /hosts		Groups and Hosts
> /group_vars	Variables related to more then one host
> /host_vars	Variables related to a single host
