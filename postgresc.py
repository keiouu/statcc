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

CARBON_SERVER = '**.**.**.***'
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

now = int( time.time() )

lines = []
lines.append('atlas.load.numbackends %d %d' % (stat[2], now))
lines.append('atlas.load.xact_commit %d %d' % (stat[3], now))
lines.append('atlas.load.xact_rollback %d %d' % (stat[4], now))
lines.append('atlas.load.blks_read %d %d' % (stat[5], now))
lines.append('atlas.load.blks_hit %d %d' % (stat[6], now))
lines.append('atlas.load.tup_returned %d %d' % (stat[7], now))
lines.append('atlas.load.tup_fetched %d %d' % (stat[8], now))
lines.append('atlas.load.tup_inserted %d %d' % (stat[9], now))
lines.append('atlas.load.tup_updated %d %d' % (stat[10], now))
lines.append('atlas.load.tup_deleted %d %d' % (stat[11], now))
lines.append('atlas.load.conflicts %d %d' % (stat[12], now))
lines.append('atlas.load.size %d %d' % (stat[14], now))

message = '\n'.join(lines) + '\n' #all lines must end in a newline
sock.sendall(message)
sock.close()
