# LXD Cloud

*LXD Cloud provides lightweight server management using the power of LXD and Ansible.*

# Features
+ Automated host machine provisioning and configuration
+ Automated container provisioning and configuration
+ Automated host machine updates
+ Automated supervised container updates
+ Automated per server and container backups with hardlink rotates (drastically reduce incremental backup downtime and size)
+ Automated KIOSK provisioning
+ Automated Nagios integration

# Quickstart

LXD is available on [Ansible  Galaxy Listing](https://galaxy.ansible.com/hxtree/lxd_cloud)

Install with Ansible Galaxy
```
$ ansible-galaxy collection install hxtree.lxd_cloud
```

# Ansible Installation

Ansible is required to run this collection. If you don't already have Ansible installed, complete the following:

On Ubuntu
```
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo apt-add-repository --yes --update ppa:ansible/ansible
$ sudo apt install ansible
```

On RHEL and CentOS:

```shell script
$ sudo yum install ansible
```

On Fedora:

```
$ sudo dnf install ansible
```

```
$ cd /etc/ansible
```

```
$ git clone https://github.com/hxtree/LXD-Cloud
```

## System Configuration
Setup each of the following Ansible files. For additional information reference [Ansible documentation](https://docs.ansible.com/).

Setup listing of Groups and Hosts
```shell script
$ vim /etc/ansible/hosts
```

Setup variables related to more then one host
```shell script
$ vim /etc/ansible/group_vars
```

Setup variables related to a single host
```shell script
$ /etc/ansible/host_vars
```
