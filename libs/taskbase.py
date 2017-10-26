#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-25 10:19
import time


class TaskBase(object):
    def __init__(self):
        pass
        # self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")

    def __call__(self, *args, **kwargs):
        dt = time.time()
        # self.logger.info("start: {}".format(self.__class__.__name__))
        self.start(*args, **kwargs)
        # self.logger.info("end at {} s".format(str(time.time() - dt)))

    def start(self, *args, **kwargs):
        raise NotImplemented()
