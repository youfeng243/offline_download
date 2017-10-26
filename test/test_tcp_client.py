#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 14:17

import socket
import time

HOST = '127.0.0.1'    # The remote host
PORT = 8000           # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.sendall(b'b'*1024*1024)
time.sleep(5)
s.sendall('ord! \n')
"""
data = s.recv(1024)

print 'Received', repr(data)
data = s.recv(1024)

print 'Received', repr(data)
"""
time.sleep(1)
s.close()