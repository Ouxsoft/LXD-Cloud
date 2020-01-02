# LXD Cloud

*LXD Cloud provides lightweight server management using the power of LXD and Ansible.*

![GitHub](https://img.shields.io/github/license/hxtree/LXD-Cloud)
![GitHub issues](https://img.shields.io/github/issues/hxtree/LXD-Cloud)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/hxtree)

# Features
+ Automated host machine provisioning and configuration
+ Automated container provisioning and configuration
+ Automated host machine updates
+ Automated supervised container updates
+ Automated per server and container backups with hardlink rotates (drastically reduce incremental backup downtime and size)
+ Automated KIOSK provisioning
+ Automated Nagios integration

# Quickstart

LXD Cloud is available on [Ansible  Galaxy Listing](https://galaxy.ansible.com/hxtree/lxd_cloud)

Install with Ansible Galaxy
```
$ ansible-galaxy collection install hxtree.lxd_cloud
```


# Ansible Installation

If you're not running Ansible already, following these instructions to install:

On Ubuntu:
```
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt install ansible
```

On RHEL and CentOS:
```
$ sudo yum install ansible
```

On Fedora:
```
$ sudo dnf install ansible
```

Next, clone LXD Cloud repo:
```
$ cd /etc/ansible/
$ git clone https://github.com/hxtree/LXD-Cloud
```

Setup listing of Groups and Hosts (reference [Ansible docs](https://docs.ansible.com/)):
```
$ vim /etc/ansible/hosts
```

Setup variables related to more then one host (reference [Ansible docs](https://docs.ansible.com/)):
```
$ vim /etc/ansible/group_vars
```

Setup variables related to a single host (reference [Ansible docs](https://docs.ansible.com/)):
```
$ /etc/ansible/host_vars
```

Set ansible.cfg remote tmp to avoid user permissions issues
```
remote_tmp = /tmp/.ansible-${USER}/tmp
```

# Contribute
Please refer to [CONTRIBUTING.md](https://github.com/hxtree/LXD-Cloud/blob/master/.github/workflows/CONTRIBUTING.md) 
for information on how to contribute to LXD Cloud.
