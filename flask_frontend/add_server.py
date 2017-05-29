import sys
from models.servers import Server
from models import storage
import datetime
import uuid

def add_server(ip, name, region):
    new_server = Server(uuid.uuid4(), ip, region, name)
    storage.new(new_server)
    storage.save()
    
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: {} (ip) (name) (region)".format(sys.argv[0]))
        exit(-1)
    add_server(sys.argv[1], sys.argv[2], sys.argv[3])
    
