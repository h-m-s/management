#!/usr/bin/env bash
# Ties together digitalocean.py which creates a new droplet with default settings,
# and fabric_install_puppet.py, which sets up Puppet on the new droplet.
#
# Needs no argument since it uses the default settings to create the droplet,
# but fabric3 + dependancies need to be installed, and a puppet server needs to be
# running locally.
#
# Make sure to edit puppet.conf with the correct configuration, as the fabfile
# will copy this to the new node.

SSH_KEY="~/.ssh/puppet"

exec 5>&1
RETURN=$(python3 digitalocean.py create-default | tee >(cat - >&5))
HOST_IP=$(echo $RETURN|cut -f2 -d":")
HOST_NAME=$(echo $RETURN|cut -f1 -d":")

fab -f fabric_install_puppet.py -i$SSH_KEY -H$HOST_IP --connection-attempts=10 setup:$HOST_NAME
