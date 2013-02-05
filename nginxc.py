import urllib2
import re
import sys
import time
import os
import platform
import subprocess
from socket import socket

CARBON_SERVER = '10.10.11.133'
CARBON_PORT = 2003

sock = socket()
try:
    sock.connect((CARBON_SERVER,CARBON_PORT))
except:
    print "Couldn't connect to %(server)s on port %(port)d" % {'server':CARBON_SERVER, 'port':CARBON_PORT}
    sys.exit(1)

now = int( time.time() )

activeConnectionsRE = re.compile(r'Active connections: (?P<conn>\d+)')
totalConnectionsRE = re.compile('^\s+(?P<conn>\d+)\s+'
                                + '(?P<acc>\d+)\s+(?P<req>\d+)')
connectionStatusRE = re.compile('Reading: (?P<reading>\d+) '
                                + 'Writing: (?P<writing>\d+) '
                                + 'Waiting: (?P<waiting>\d+)')
req = urllib2.Request('http://localhost:8090/nginx_status')

lines = []

try:
	handle = urllib2.urlopen(req)
	for l in handle.readlines():
		l = l.rstrip('\r\n')
		if activeConnectionsRE.match(l):
			lines.append("servers.Nomos.active_connections %d %d" % (int(activeConnectionsRE.match(l).group('conn')), now))
		elif totalConnectionsRE.match(l):
			m = totalConnectionsRE.match(l)
			req_per_conn = float(m.group('req')) / float(m.group('acc'))
			lines.append("servers.Nomos.conn_accepted %d %d" % (int(m.group('conn')), now))
			lines.append("servers.Nomos.conn_handled %d %d" % (int(m.group('acc')), now))
			lines.append("servers.Nomos.req_handled %d %d" % (int(m.group('req')), now))
			lines.append("servers.Nomos.req_per_conn %f %d" % (float(req_per_conn), now))
		elif connectionStatusRE.match(l):
			m = connectionStatusRE.match(l)
			lines.append("servers.Nomos.act_reads %d %d" % (int(m.group('reading')), now))
			lines.append("servers.Nomos.act_writes %d %d" % (int(m.group('writing')), now))
			lines.append("servers.Nomos.act_waits %d %d" % (int(m.group('waiting')), now))
except IOError, e:
	pass
except Exception, e:
	pass

message = '\n'.join(lines) + '\n'

#all lines must end in a newline
sock.sendall(message)
sock.close()