import sys
import time
import os
import platform
import subprocess
from socket import socket

CARBON_SERVER = '10.10.11.133'
CARBON_PORT = 2003

def get_loadavg():
    # For more details, "man proc" and "man uptime"      
        if platform.system() == "Linux":
            return open('/proc/loadavg').read().strip().split()[:3]
        else:
            command = "uptime"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            os.waitpid(process.pid, 0)
            output = process.stdout.read().replace(',', ' ').strip().split()
            length = len(output)
            return output[length - 3:length]


sock = socket()
try:
    sock.connect((CARBON_SERVER,CARBON_PORT))
except:
    print "Couldn't connect to %(server)s on port %(port)d" % {'server':CARBON_SERVER, 'port':CARBON_PORT}
    sys.exit(1)

now = int( time.time() )
lines = []
# We're gonna report all three loadavg values
loadavg = get_loadavg()
lines.append("cronus.load.avg_1min %s %d" % (loadavg[0],now))
lines.append("cronus.load.avg_5min %s %d" % (loadavg[1],now))
lines.append("cronus.load.avg_15min %s %d" % (loadavg[2],now))

message = '\n'.join(lines) + '\n'
#all lines must end in a newline
sock.sendall(message)
sock.close()