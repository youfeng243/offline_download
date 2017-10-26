#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-27 11:35
import sys
from logging.handlers import RotatingFileHandler

sys.path.append("..")
import logging
from conf import m_settings
import os


# 每一个task实例一个logger
def getLogger(task_name="root", level=logging.INFO, console_out=False):
    logger = logging.getLogger("root")
    if isinstance(level, basestring):
        level = level.lower()
    if level == "debug":
        level = logging.DEBUG
    elif level == "info":
        level = logging.INFO
    elif level == "warning":
        level = logging.WARNING
    elif level == "error":
        level = logging.ERROR
    else:
        level = logging.INFO

    if not os.path.exists(m_settings.LOGDIR):
        os.makedirs(m_settings.LOGDIR)
    LOG_FILE = m_settings.LOGDIR + "/%s.log" % task_name
    fmt = "%(asctime)s - %(filename)s[line:%(lineno)d] %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=64 * 1024 * 1025, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if console_out is True:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger
