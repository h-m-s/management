import sys
import subprocess
from models import storage
from models.servers import Server

def ping_telnet_server(ip):
    p1 = subprocess.Popen(["echo", "''"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["nc", "-q1", "-w1", "{}".format(ip), "23"],
                          stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    results = p2.communicate()[0]
    results = results.split()
    if results == []:
        return(False)
    last_line = results[-1].decode('utf-8')
    if "Password:" not in last_line:
        return(False)
    else:
        return(True)
                                                                        
def check_servers():
    server_list = [server for server in storage.session.query(Server)]

    servers = []
    ip_list = []
    for server in server_list:
        if server.ip in ip_list:
            continue
        if ping_telnet_server(server.ip) is True:
            servers += [{'ip': server.ip,
                         'region': server.region,
                         'status': 'Up'}]
        else:
            servers += [{'ip': server.ip,
                         'region': server.region,
                         'status': 'Down!'}]
        ip_list += [server.ip]
    return(servers)

if __name__ == '__main__':
    check_servers()
