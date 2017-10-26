#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time: 2017/5/24 上午11:18
@Author: six
@File: command_main.py
"""
import sys

# import gevent.pool
# from gevent import monkey
#
# monkey.patch_all()

from multiprocessing.dummy import Pool as ThreadPool

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from libs.loghandler import getLogger

logger = getLogger("command_main", console_out=True, level="debug")

# from bygzjy_public_resource_tender import BygzjyPublicResourceTenderWorker
# from gnggzyjy_public_resource_tender import GnggzyjyPublicResourceTenderWorker
# from lanzhou_public_resource_tender import LanzhouPublicResourceTenderWorker
# from lnsggzyjy_public_resource_tender import LnsggzyjyPublicResourceTenderWorker
# from lxggzyjy_public_resource_tender import LxggzyjyPublicResourceTenderWorker
# from plsggzyjy_public_resource_tender import PlsggzyjyPublicResourceTenderWorker
# from tsggzyjy_public_resource_tender import TsggzyjyPublicResourceTenderWorker
# from wwggzy_public_resource_tender import WwggzyPublicResourceTenderWorker
# from online_task import LzcourtTask

from sites.bid_detail.gsggzyjy.bygzjy_public_resource_tender import BygzjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.gnggzyjy_public_resource_tender import GnggzyjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.lanzhou_public_resource_tender import LanzhouPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.lnsggzyjy_public_resource_tender import LnsggzyjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.lxggzyjy_public_resource_tender import LxggzyjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.online_task import LzcourtTask
from sites.bid_detail.gsggzyjy.plsggzyjy_public_resource_tender import PlsggzyjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.tsggzyjy_public_resource_tender import TsggzyjyPublicResourceTenderWorker
from sites.bid_detail.gsggzyjy.wwggzy_public_resource_tender import WwggzyPublicResourceTenderWorker

__all__ = ["BygzjyPublicResourceTenderWorker", "GnggzyjyPublicResourceTenderWorker",
           "LanzhouPublicResourceTenderWorker", "LnsggzyjyPublicResourceTenderWorker",
           "LxggzyjyPublicResourceTenderWorker", "PlsggzyjyPublicResourceTenderWorker",
           "TsggzyjyPublicResourceTenderWorker", "WwggzyPublicResourceTenderWorker",
           "LzcourtTask"]


def do_work():
    logger.info("启动多线程进行抓取...")
    thread_num = len(__all__)
    thread_pool = ThreadPool(processes=thread_num)
    for clazz in __all__:
        thread_pool.apply_async(eval(clazz)().start)
    thread_pool.close()

    logger.info("线程加载完成, 等待执行完成...")
    thread_pool.join()

    logger.info("所有线程执行完成...结束进程")
    exit(0)


if __name__ == "__main__":
    do_work()
