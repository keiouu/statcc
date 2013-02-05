#!/usr/bin/python
"""Copyright 2008 Orbitz WorldWide

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import sys
import time
import os
import platform 
import subprocess
import psycopg2
from socket import socket

CARBON_SERVER = 'localhost'
CARBON_PORT = 2003

sock = socket()
try:
  sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
  sys.exit(1)

conn = psycopg2.connect("dbname=postgres user=postgres")
cur = conn.cursor()


cur.execute("SELECT pg_stat_database.*, \
                pg_database_size(pg_database.datname) AS size \
                FROM pg_database JOIN pg_stat_database \
                ON pg_database.datname = pg_stat_database.datname \
                WHERE pg_stat_database.datname \
                NOT IN ('template0','template1','postgres')")
stats = cur.fetchall()


cur.execute("SELECT datname, count(datname) \
                FROM pg_stat_activity GROUP BY pg_stat_activity.datname;")
connections = cur.fetchall()

now = int( time.time() )

lines = []

ret = {}
for stat in stats:
	info = {'numbackends': stat[2],
            'xact_commit': stat[3],
            'xact_rollback': stat[4],
            'blks_read': stat[5],
            'blks_hit': stat[6],
            'tup_returned': stat[7],
            'tup_fetched': stat[8],
            'tup_inserted': stat[9],
            'tup_updated': stat[10],
            'tup_deleted': stat[11],
            'conflicts': stat[12],
            'size': stat[14]}

	database = stat[1]
	ret[database] = info

for database in ret:
	for (metric, value) in ret[database].items():
		lines.append('atlas.databases.%s.%s %d %d' % (database, metric, value, now))

for (database, connection) in connections:
	lines.append('atlas.databases.%s.connections %d %d' % (database, connection, now))

message = '\n'.join(lines) + '\n' #all lines must end in a newline
sock.sendall(message)
sock.close()
