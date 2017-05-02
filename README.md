Included in this repo are several scripts for managing H-M-S (with more to come):

digitalocean.py: Uses Digital Ocean API to spin up new droplets. Not specifically H-M-S related, but can be used in conjunction with other scripts. Requires your Digital Ocean API key to be set to the environment variable digitalocean, and requests to be installed (pip3 install requests).

Flags:
	create: Creates a new Digital Ocean droplet, walking you through prompts for name, region, size, image (distro images only) and SSH key.
	add-key <key_file> <name for SSH key>: Adds a new key to your Digital Ocean account.
	list-droplets: Lists all droplets associated with your API key.
	ips <name (optional)>: Shows all droplet names/IPs for your account, or just a single droplet if a droplet name is specified.
	create-default: Quickly creates a new droplet with default settings. Does not prompt for anything. Defaults can be changed to your liking for create-default, with default settings will create a 512mb droplet on sfo2 with Ubuntu 14-04, using an SSH key on Digital Ocean called 'puppet', and the name prefix honey-#.

fabric_install_puppet.py: Uses Fabric3 to install Puppet. Assumes Ubuntu 14.04 (will support more later) and that you have a default puppet.conf file in the same directory. Should be ran from your Puppet server: script automatically runs agent --test, locally signs the cert, and then runs agent -t to provision.

Warning: If you have used the same hostname before, be sure to purge the certs before running this script. Otherwise, you will need to puppet cert clean and rerun puppet agent -t.

new_droplet.sh: Requires digitalocean.py, fabric_install_puppet.py and puppet.conf in the same folder as the script. Running new_droplet will create a droplet with digitalocean.py and install puppet using fabric_install_puppet. This should bring you from no server, to an empty Droplet, to installing Puppet, to allowing the Puppet server to provision the droplet and finally to a running server with the telnet-honeypot and wificam honeypot.

Included in the puppet directory are sample manifests for Puppet. These manifests automatically pull both the telnet-honeypot and wificam repos, install dependancies, and start the servers.
