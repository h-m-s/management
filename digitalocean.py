#!/usr/bin/python3
"""
Module to handle using Digital Ocean API to manage droplets.
Requires your Digital Ocean API key to be set to the digitalocean
environmental variable.
"""
import json
import os
import requests
import sys
from time import sleep
"""
Set default values here. Set them to None if you'd rather
not use default values.

Default name prefix is used in case you have a numbered
naming scheme for your honeypot droplets.

If you do, set your default name prefix here and this
script will select the next number automatically for
the default value. Otherwise you can manually
enter the name for the new server.
"""
default_name_prefix = "honey-"
default_region = "sfo2"
default_size = "512mb"
default_image = "ubuntu-14-04-x64"
default_ssh_key = "puppet"

api = os.getenv('digitalocean')
headers = {'Authorization': 'Bearer {}'.format(api),
           'Content-Type': 'application/json'}
api_url = "https://api.digitalocean.com/v2/"
flags = {
    'create': ['create',
               'Creates a new Digital Ocean droplet.'],
    'add-key': ['add-key <key_file> <name>',
                'Adds a new SSH key to Digital Ocean under the given name.'],
    'list-droplets': ['list-droplets',
                      ("Lists all Digital Ocean droplets"
                       " associated with API key.")],
    'ips': ['ips <optional_name>',
            ("Returns the IPV4 address for a given droplet, "
             "or for all droplets if no argument passed.")],
    'available-images': ['available-images',
                         ("Prints a list of all available images. "
                          "Distro images only, not including apps "
                          "or snapshots.")],
    'create-default': ['create-default',
                       ("Creates an image with the default settings. "
                        "WARNING: Will not give any prompts! Output will be "
                        "new droplet IP, or error message if failure.")]
}


class Droplet():
    """
    Droplet class, currently only used to print a good repr for droplets
    from list_droplets.

    Could easily be extended to do a little bit more in the future.
    """
    def __init__(self, droplet_json):
        self.name = droplet_json['name']
        self.id = droplet_json['id']
        self.region = droplet_json['region']['name']
        self.distro = droplet_json['image']['distribution']
        self.distro_name = droplet_json['image']['name']
        self.size = droplet_json['size']
        self.ip = droplet_json['networks']['v4'][0]['ip_address']
        self.status = droplet_json['status']

    def __repr__(self):
        rep = "Droplet name: {}\nID: {}\n".format(self.name, self.id)
        rep += "Region: {}\n".format(self.region)
        rep += "Distro: {} {}\n".format(self.distro, self.distro_name)
        rep += "IP address: {}\n".format(self.ip)
        rep += "Status: {}\n".format(self.status)
        return(rep)


def list_droplets():
    """
    Lists available droplets.
    """
    droplets = api_call('droplets')['droplets']
    for droplet_data in droplets:
        print('-----')
        new_droplet = Droplet(droplet_data)
        print(new_droplet)


def print_droplet_ips():
    """
    Prints the IP addresses associated with each droplet,
    or prints all if no name specified.
    """
    droplets = api_call('droplets')['droplets']
    if len(sys.argv) == 2:
        for droplet in droplets:
            for network in droplet['networks']['v4']:
                print("{}: {}".format(droplet['name'], network['ip_address']))
    else:
        for droplet in droplets:
            if droplet['name'] == sys.argv[2]:
                for network in droplet['networks']['v4']:
                    print(network['ip_address'])
                exit(1)
        print("No droplet found with the given name: {}".format(sys.argv[2]))


def api_call(entry):
    """
    Grabs info from the Digital Ocean API, returns the JSON.

    If we get a 401 we'll assume it's a bad API key and exit out.
    """
    r = requests.get("{}/{}".format(api_url, entry), headers=headers)
    if r.status_code == 401:
        print("Unable to authenticate to DigitalOcean.")
        print("Please check that your API key is in the digitalocean env.")
        exit(-1)
    return(r.json())


def get_next_droplet_number():
    """
    If default_name_prefix is correct this will look at what servers you
    already have and select the next available number.

    For instance, if you have honey-1 and honey-2 it should select 3 for the
    next droplet.
    """
    r = api_call('droplets')
    try:
        droplets = r['droplets']
    except KeyError as err:
        droplets = None
    honey_droplets = []

    if droplets is not None:
        for droplet_name in [x['name'] for x in droplets]:
            if default_name_prefix in droplet_name:
                honey_droplets += [droplet_name]
        droplets = [droplet[droplet.find('-') + 1:] for
                    droplet in honey_droplets]
        return(int
               (max
                ([droplet for droplet in droplets if droplet.isdigit()])) + 1)
    else:
        return(1)


def get_droplet_name():
    """
    Input loop for getting name for new droplet.
    """
    next_droplet_number = get_next_droplet_number()
    default_name = "{}{}".format(default_name_prefix,
                                 next_droplet_number)
    print('Name for droplet?')
    droplet_name = input(
        '(Press enter for default value of {}): '.format(
            default_name))
    if droplet_name == '':
        droplet_name = default_name
    return(droplet_name)


def get_droplet_region(regions):
    """
    Input loop for getting region for new droplet.

    Shows available regions.
    """
    slugs = [x['slug'] for x in regions]
    print("Available regions:")
    print(slugs)
    print('Region for droplet?')
    while 1:
        droplet_region = input(
            '(Press enter for default value of {}): '.format(
                default_region))
        if droplet_region == '':
            return(default_region)
        if droplet_region in slugs:
            return(droplet_region)
        print('Not a valid region.')


def get_available_regions():
    """
    Gets a list of available regions.
    """
    r = api_call('regions')
    return(r['regions'])


def get_droplet_size(droplet_region, regions):
    """
    Input loop to choose droplet size.

    Will print available sizes for the previously chosen region.

    Droplet_region is the chosen region, regions is a pre-generated
    list of available regions.
    """
    available_sizes = get_available_sizes(droplet_region, regions)
    print("Available sizes for {}:".format(droplet_region))
    print(available_sizes)
    print("Chosen size?")
    while 1:
        droplet_size = input(
            '(Press enter for default value of {}): '.format(
                default_size))
        if droplet_size == '':
            return(default_size)
        if droplet_size in available_sizes:
            return(droplet_size)


def get_available_sizes(droplet_region, regions):
    """
    Gets a list of sizes available for the given region.
    """
    for region in regions:
        if region['slug'] == droplet_region:
            return(region['sizes'])


def get_droplet_image():
    """
    Input loop to get image for droplet.
    """
    print("Select image to use for droplet.")
    available_images = get_available_images()
    while (True):
        droplet_image = input(("(? for available images, "
                               "enter for default value of {}"
                               " or use shorthand name.) ".format(
                                   default_image)))
        if droplet_image == "":
            droplet_image = default_image
        for image in available_images:
            if image[0] == droplet_image:
                return(image)
        if droplet_image == "?":
            print_available_images()
        else:
            print("Unknown image for droplet.")


def get_droplet_ssh_key():
    """
    Input loop to get SSH keys available for droplet.

    SSH keys need to be added to Digital Ocean first.
    If none available, will skip adding an SSH key.
    """
    keys = api_call('account/keys')['ssh_keys']
    print("Available SSH keys:")
    try:
        available_keys = [[x['name'], x['id']] for x in keys]
        print([key[0] for key in available_keys])
    except:
        print("None available, skipping.")
        return (None)
    while (1):
        droplet_ssh_key = input((
            "(Choose key, type none for no key, "
            "or enter for default value of {}): ".format(default_ssh_key)))
        if droplet_ssh_key == "":
            droplet_ssh_key = default_ssh_key
        for key in available_keys:
            if key[0] == droplet_ssh_key:
                return(key)
        if droplet_ssh_key == 'none':
            return (None)


def print_usage(flag=None):
    """
    Prints usage info.

    Snags info from a dictionary containing available flags and description.
    Passing an argument will print usage specific information about a flag.
    """
    if flag is None:
        print("Usage: {} <flag>".format(sys.argv[0]))
        print("Available flags:")
        for x in flags.keys():
            print("\t{}: {}".format(flags[x][0], flags[x][1]))
    else:
        print("Usage:".format(sys.argv[0]))
        print("\t{}: {}".format(flags[flag][0], flags[flag][1]))
    exit(2)


def create_droplet_prompts():
    """
    Creates a droplet from given information.
    """
    regions = get_available_regions()
    droplet_name = get_droplet_name()
    droplet_region = get_droplet_region(regions)
    droplet_size = get_droplet_size(droplet_region, regions)
    droplet_ssh_key = get_droplet_ssh_key()
    droplet_image = get_droplet_image()

    print("\nChosen droplet specs:\n",
          "\tName: {}\n".format(droplet_name),
          "\tRegion: {}\n".format(droplet_region),
          "\tSize: {}\n".format(droplet_size),
          "\tKey: {}\n".format(droplet_ssh_key[0]),
          "\tImage: {}\n".format(droplet_image[0]))

    print("Are you sure you'd like to create this droplet?")
    while True:
        answer = input("Type yes to create droplet, or no to cancel: ")
        if answer == 'yes':
            new_drop_ip = create_new_droplet(droplet_name,
                                             droplet_region,
                                             droplet_size,
                                             droplet_ssh_key[1],
                                             droplet_image[1])
            print("Created droplet successfully!")
            print("{}: {}".format(droplet_name, new_drop_ip))
            exit()
        elif answer == 'no':
            print("Exiting without creating new droplet.")
            exit(1)


def create_default_droplet():
    """
    Creates a new droplet with default settings and prints only the hostname and IP.

    Mainly for using in concert with other orchestration like Puppet.
    """
    keys = api_call('account/keys')['ssh_keys']
    for key in keys:
        if key['name'] == default_ssh_key:
            droplet_ssh_key = key['id']
    droplet_name = "{}{}".format(default_name_prefix,
                                 get_next_droplet_number())
    new_drop_ip = create_new_droplet(
        droplet_name,
        default_region,
        default_size,
        droplet_ssh_key,
        default_image,
        silent=True)
    print("{}:{}".format(droplet_name, new_drop_ip))


def create_new_droplet(name, region, size, ssh_key, image, silent=False):
    """
    Sends the actual POST request to create a new droplet.
    """
    data = {"name": name,
            "region": region,
            "size": size,
            "ssh_keys": [ssh_key],
            "image": image}
    r = requests.post("{}droplets".format(api_url),
                      headers=headers,
                      data=json.dumps(data))
    if r.status_code == 202:
        if silent is False:
            print("Droplet created successfully, waiting for IP...")
        new_droplet_id = r.json()['droplet']['id']
        while(True):
            sleep(15)
            r = api_call('droplets/{}'.format(new_droplet_id))
            try:
                return(r['droplet']['networks']['v4'][0]['ip_address'])
            except KeyError as err:
                if silent is False:
                    print("Waiting for IP...")
    else:
        print("Error creating new droplet: {}".format(r.json()))
        exit(2)


def add_ssh_key():
    """
    Adds an SSH key to Digital Ocean.

    SSH key must be provided in sys.argv as the second argument passed.
    """
    if len(sys.argv) < 4:
        print_usage('add-key')
        exit(2)
    key = sys.argv[2]
    key_name = sys.argv[3]
    if not os.path.isfile(key):
        print("Invalid SSH key.")
        exit(2)
    if not os.access(key, os.R_OK):
        print("Unable to open SSH key for reading.")
        exit(-1)
    post_ssh_key(key, key_name)


def post_ssh_key(key, key_name):
    """
    Sends a post request with a new SSH key and handles errors.
    """
    try:
        with open(key) as fd:
            key_data = fd.read()
    except:
        print("Error reading key.")
        exit(2)
    data = {'name': key_name, 'public_key': key_data}
    p = requests.post("{}account/keys".format(api_url),
                      headers=headers,
                      data=data)
    if p.status_code == 422:
        error_message = p.json()['message']
        print("Error adding SSH key: {}".format(error_message))
        if "invalid type," in error_message:
            print("Are you sure you're adding the public key?")
        exit(-1)
    else:
        new_key_id = p.json()['ssh_key']['id']
        print("Successfully added key with id: {}".format(new_key_id))


def print_available_images():
    """
    Prints available images.
    Distro images only at the minute, since that's all I normally use.
    """
    for image in api_call('images?type=distribution')['images']:
        print("{}: {}{}".format(
            image['slug'],
            image['distribution'],
            image['name']))


def get_available_images():
    """
    Builds a list of available images.
    """
    return ([[image['slug'], image['id']] for image in api_call(
        'images?type=distribution')['images']])


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] not in flags:
        print_usage()
    elif sys.argv[1] == "create":
        create_droplet_prompts()
    elif sys.argv[1] == "add-key":
        add_ssh_key()
    elif sys.argv[1] == "list-droplets":
        list_droplets()
    elif sys.argv[1] == "available-images":
        print_available_images()
    elif sys.argv[1] == "ips":
        print_droplet_ips()
    elif sys.argv[1] == "create-default":
        create_default_droplet()
