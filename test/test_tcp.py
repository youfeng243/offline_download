#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 14:16
import functools
import threading

import tornado
from tornado import iostream
from tornado.netutil import bind_sockets
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado import gen
import inspect
class Connection(object):
    clients = set()

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self.read_message()
        print "A new user has entered the chat room.", address

    def read_message(self):
        f = self._stream.read_until('\n', self.broadcast_messages)
        print inspect.stack()

    def broadcast_messages(self, data):
        print "User said:", data[:-1], self._address
        for conn in Connection.clients:
            conn.send_message(data)
        self.read_message()

    def send_message(self, data):
        self._stream.write(data)

    def on_close(self):
        print "A user has left the chat room.", self._address
        Connection.clients.remove(self)


import os
class ChatServer(TCPServer):
    """
@gen.coroutine
def handle_stream(self, stream, address):
    print "process:%d" % os.getpid(), "New connection :", address, stream
    Connection(stream, address)
    print "connection num is:", len(Connection.clients)
"""

    @gen.coroutine
    def handle_stream(self, stream, address):
        #conn = PubConnection(stream, address, self.io_loop)
        while 1:
            try:
                # data=yield stream.read_until(conn.m_EOF)
                data = yield stream.read_bytes(1024 * 1024, partial=True)
                print "data",len(data)
            except (iostream.StreamClosedError, iostream.UnsatisfiableReadError):
                return
            except Exception as e:
                return


if __name__ == '__main__':
    print "Server start ......"
    sockets = bind_sockets(8000)
    tornado.process.fork_processes(0)
    server = ChatServer()
    server.add_sockets(sockets)
    IOLoop.current().start()




def multi_thread_singleton(cls, *args, **kwargs):
    instance = {}
    instance_lock = threading.Lock()
    @functools.wraps(cls)
    def _singleton(*args, **kwargs):
        if cls in instance:return instance[cls]
        with instance_lock:
            instance[cls] =cls(*args, **kwargs)
            return instance[cls]
    return _singleton


@multi_thread_singleton
class Test():
    pass

t = Test()
print id(t)
t = Test()
print id(t)