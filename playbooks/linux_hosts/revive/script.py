#!/usr/bin/python
from __future__ import with_statement
from optparse import OptionParser
import inspect, os, shutil
import subprocess
import socket
import string
import sys 
import json

def main():
        lxd_host = str(socket.gethostname())
        lxc_path = "/var/lib/lxd/containers" # where do the containers live
    
        info_raw = shell_exec('lxc list --format="json"') #--columns="s4" --format="json"')
        info = json.loads(info_raw)    
        for container in info:
                print container['name'] + ' ',

                # handle running
                if container['status'] == 'Running':
                        print 'running',

                        # get container ip_addr                 
                        if keys_exists(container, 'state', 'network', 'eth0', 'addresses',0,'address'):
                                ip_addr = container['state']['network']['eth0']['addresses'][0]['address']
                        else: 
                                ip_addr = ''

                        # check ip_addr valid
                        if ipv4_address_valid(ip_addr):
                                print ' on ' + ip_addr
                                continue
                        else:
                                # if container does not have a valid ip_addr and is running restart
                                print ' without ip -- restart requested'
                                print shell_exec('lxc restart ' + container['name'])               

                # handle stopped
                elif container['status'] == 'Stopped':
                        print 'stopped'
                        continue
 
                # handle error
                elif container['status'] == 'Error':
                        # if container state is Error restart
                        print 'state error -- restart requested'
                        print shell_exec('lxc restart ' + container['name'])
                        continue

                # handle unhandled
                else:
                        print 'state unhandled: ' + container['status']

        exit()

# A convenience method that takes a string or array in the formate expected by subprocess.popen
# and returns the stdout, displaying any stderr if one occurs 
def shell_exec(command):
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        if errors:
                raise Exception("ERROR: " + errors)
        return output

# validate if ip4 address
def ipv4_address_valid(address):
        try:
                socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here
                try:
                        socket.inet_aton(address)
                except socket.error:
                        return False
                return address.count('.') == 3
        except socket.error:  # not a valid address
                return False
        return True

# check if key exists
def keys_exists(element, *keys):

        # validate parameters
        if type(element) is not dict:
                raise AttributeError('keys_exists() expects dict as first argument.')
        if len(keys) == 0:
                raise AttributeError('keys_exists() expects at least two arguments but one given.')

        # validate keys
        _element = element
        for key in keys:
                try:
                        _element = _element[key]
                except:
                        return False
        return True

# run things
if __name__ == "__main__":
        main()

