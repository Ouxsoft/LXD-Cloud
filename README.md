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
Install Ansible

On Ubuntu
```shell script
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

```shell script
$ sudo dnf install ansible
```

```shell script
$ cd /etc/ansible
```

```shell script
$ git clone https://github.com/hxtree/LXD-Cloud
```

## System Configuration
Setup each of the following Ansible files. For additional information reference [Ansible documentation](https://docs.ansible.com/).

Groups and Hosts
```shell script
$ vim /etc/ansible/hosts
```

Variables related to more then one host
```shell script
$ vim /etc/ansible/group_vars
```

Variables related to a single host
```shell script
$ /etc/ansible/host_vars
```
