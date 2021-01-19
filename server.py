#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from NetThermPrintServer import NetThermPrintServer

server = NetThermPrintServer('0.0.0.0', 41230, 41231, 'printqueue.db', True)
server.start()


