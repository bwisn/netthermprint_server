#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import urlparse
from urllib.parse import parse_qs
import time
import random

server_address = '0.0.0.0'
server_port = 41230
http_port = 41231
dbpath = 'printqueue.db'
debug = True


class NetThermPrintServer:
    class HTTPServerReqHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type','text/html')
            self.end_headers()
            bits = parse_qs(urlparse(self.path).query)
            if ('title' and 'content' and 'special' in bits):
                title = ''.join(bits['title'])
                content = ''.join(bits['content'])
                special = ''.join(bits['special'])
                unixtime = str(int(time.time()))
                notifyid = str(random.randint(1, 9999))
                outstr = "PRINT;" + notifyid + ";" + unixtime + ";" + title + ";" + content + ";" + special
                outstr = outstr.replace("\n", "\\n") # escape newlines
                print(outstr)
                dbfile = open(dbpath, 'a')
                dbfile.write(outstr)
                dbfile.close()
            return


    def __init__(self, address, server_port, http_port, dbpath, debug):
        self.server_address = address
        self.server_port = server_port
        self.http_port = http_port
        self.dbpath = dbpath
        self.debug = debug

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = (self.server_address, self.server_port)
        sock.bind(server)
        httpd = HTTPServer((self.server_address, self.http_port), self.HTTPServerReqHandler)
        thread = threading.Thread(target = httpd.serve_forever)
        thread.daemon = True
        thread.start()

        print("Listening on " + self.server_address + ":" + str(self.server_port) + " and HTTP on port: " + str(self.http_port))

        busytimestamp = 0
        okrcvd = True
        id_wait = 0

        while True:
            payload, client_address = sock.recvfrom(16384)
            payload = payload.decode('utf-8')
            print(payload)

            if (payload == "REQ_ALL"):
                if (okrcvd) :
                    if os.path.exists(os.path.realpath(dbpath))and os.path.getsize(os.path.realpath(dbpath)) > 0:
                        dbfile = open(dbpath, 'r')
                        firstline = dbfile.readline().strip()
                        sock.sendto(str.encode(firstline), client_address)
                        okrcvd = False
                        dbfile.close()

            if (payload.startswith('BUSY')):
                id = payload.split(" ",1)[1]
                waitingresp = "WAITING " + id
                id_wait = id
                sock.sendto(str.encode(waitingresp), client_address)
                busytimestamp = int(time.time())
                okrcvd = False

            if (payload.startswith('OK')):
                id = payload.split(" ",1)[1]
                if os.path.exists(os.path.realpath(dbpath))and os.path.getsize(os.path.realpath(dbpath)) > 0:
                    dbfile = open(dbpath, 'r')
                    lines = dbfile.readlines()
                    dbfile.close()
                    dbfile = open(dbpath, 'w')
                    for line in lines:
                        if not line.startswith(id, 6):
                            dbfile.write(line)
                    dbfile.close()
                    okrcvd = True
                    busytimestamp = 0

            if (busytimestamp > 0 and ((int(time.time()) - busytimestamp ) != 0)  and not okrcvd):
                waitingresp = "WAITING " + str(id_wait)
                sock.sendto(str.encode(waitingresp), client_address)
                print("SENT WAITING")
