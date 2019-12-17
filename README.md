# LXD Cloud

LXD Cloud combines Ansible server automation with LXD's system container manager for lightweight server management. Features include:
+ Automated host machine provisioning and configuration
+ Automated container provisioning and configuration
+ Automated host machine updates
+ Manually update all servers with oversight
+ Server per container backups with hardlink rotates (drastically reduce incremental backup downtime and size)
+ Automated KIOSK deployment
+ Automated Nagios integration

# Quickstart
Install Ansible

On Fedora, CentOS 8

```shell script
sudo dnf install ansible
```
(see Ansible docs for other distros)

```shell script
cd /etc/ansible
```

```shell script
git clone https://github.com/hxtree/LXD-Cloud
```

## System Configuration
Setup each of the following Ansible files. For additional information reference [Ansible documentation](https://docs.ansible.com/).

```shell script
vim /hosts
```
Groups and Hosts

```shell script
vim /group_vars
```
Variables related to more then one host

```shell script
/host_vars
```
Variables related to a single host
