import sys
from models.servers import Server
from models import storage
import datetime
import uuid

def add_server(ip, name, region):
    new_server = Server(uuid.uuid4(), ip, region, name)
    storage.new(new_server)
    storage.save()

def delete_server(ip):
    print("Marking server as inactive on DB.")
    for server in storage.session.query(Server).filter(Server.ip == ip):
        server.active = False
    storage.save()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: {} (action) (ip) (name) (region)".format(sys.argv[0]))
        print("actions: add/delete")
        exit(-1)
    if 'add' in sys.argv[1]:
        add_server(sys.argv[2], sys.argv[3], sys.argv[4])
    elif 'delete' in sys.argv[1]:
        delete_server(sys.argv[2])
    
