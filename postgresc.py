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

conn = psycopg2.connect("dbname=postgres user=postgres")
cur = conn.cursor()
cur.execute("SELECT sum(xact_commit + xact_rollback) FROM pg_stat_database;")
result = cur.fetchone()

sock = socket()
try:
  sock.connect( (CARBON_SERVER,CARBON_PORT) )
except:
  print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
  sys.exit(1)

now = int( time.time() )
lines = []
lines.append("atlas.load.commits %d %d" % (result[0],now))
message = '\n'.join(lines) + '\n' #all lines must end in a newline
sock.sendall(message)

