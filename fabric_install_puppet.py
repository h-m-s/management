#!/usr/bin/python3
""" 
Fabfile for settings up Puppet.

Just FYI, may require Fabric3, unsure of Fabric2 support.

Requires the host IP to be passed in on the command line, either
as an argument to fab or when prompted.

Ex: fab -f fabric_install_puppet.py -i ~/.ssh/puppet -H9.9.9.9 setup:honey-1
"""
from fabric.api import *
import os
import sys

def setup(name):
    """
    Sets up Puppet on a new Ubuntu 14.04 instance.

    Requires the server hostname to be passed as an argument to fabric.

    """
    env.user = "root"
    run("cd ~; wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb")
    run("dpkg -i puppetlabs-release-trusty.deb")
    run("rm puppetlabs-release-trusty.deb")
    run("apt-get update")
    run("apt-get install puppet -y")
    run("sed -i \"s/no/yes/\" /etc/default/puppet")
    version = str(run("puppet help | tail -n 1"))
    version = str(version.split('\n')[-1])
    run("echo -e \"Package: puppet puppet-common puppetmaster-passenger\n" +
                  "Pin: version {:s}\n".format(str(version)) +
                  "Pin-Priority: 501 > /etc/apt/preferences.d/00-puppet.pref\"")
    put("puppet.conf", "/etc/puppet/puppet.conf")
    run("service puppet start")
    with settings(warn_only=True):
        run("puppet agent --test") # Will fail the first time around because cert won't be signed
    local("puppet cert sign {}".format(name))
    run("puppet agent --test")

if __name__ == '__main__':
    setup()
