#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-25 10:24
import time
from beanstalkc import Connection

#-*- coding: utf-8 -*-
import beanstalkc
from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.transport.TTransport import TMemoryBuffer

from threading import Lock
def thrift2bytes(obj):
    str = None
    try:
        tMemory_b = TMemoryBuffer()
        tBinaryProtocol_b = TBinaryProtocol(tMemory_b)
        obj.write(tBinaryProtocol_b)
        str = tMemory_b.getvalue()
    except EOFError, e:
        pass
    return str

class PyBeanstalk(object):
    def __init__(self, host, port=11300):
        self.host = host
        self.port = port
        self.put_lock = Lock()
        self.__conn = beanstalkc.Connection(host, port)
        self.cnt = 0
    def __del__(self):
        self.__conn.close()
    #beanstalk重连
    def reconnect(self):
        self.__conn.reconnect()

    def put(self, tube, body, priority=2**31, delay=0, ttr=10):
        try_cnt = 0
        while True:
            try_cnt += 1
            try:
                if body == None:
                    return None
                if len(body) >= 31457280:
                    return None
                with self.put_lock:
                    self.cnt += 1
                    self.__conn.use(tube)
                    result = self.__conn.put(body, priority, delay, ttr)
                    return result
            except beanstalkc.SocketError as e:
                time.sleep(1)
                self.reconnect()
                if try_cnt > 10:
                    raise e
        return None

    def reserve(self, tube, timeout=20):
        try_cnt = 0
        while True:
            try_cnt += 1
            try:
                self.__conn.watch(tube)
                job = self.__conn.reserve(10)
                if not job is None:
                    body = job.body
                    job.delete()
                    return body
            except beanstalkc.SocketError as e:
                if try_cnt > 10:
                    raise e
                time.sleep(1)
                self.reconnect()
            except Exception as e:
                raise e
        return None

    def stats_tube(self, tube):
        return self.__conn.stats_tube(tube)

    def get_tube_count(self, tube):
        return self.__conn.stats_tube(tube)["current-jobs-ready"]

if __name__ == '__main__':
    pybeanstalk = PyBeanstalk('101.201.102.37')
    job =  pybeanstalk.reserve('extract_info')
    print len(job.body)
    job.delete()
