#!/usr/bin/python
from __future__ import with_statement
import inspect, os, shutil
import subprocess
import datetime
import socket
import string
import sys

def main():
    # check if command exists
    response = shell_exec('lxc list')
    if response != False:
        
        print response
        exit()
    else:
        print shell_exec('lxc-list')
        exit()

def shell_exec(command):
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = proc.communicate()
        if errors:
                return False
        return output
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            # handle file not found error.
            return False
        else:
            return False

# run things
if __name__ == "__main__":
        main()

