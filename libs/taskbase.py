#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-25 10:19
import json
import sys
import time

import requests

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from conf.m_settings import log


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

    def get_proxy(self):

        proxy_url = 'http://101.132.128.78:18585/proxy'

        user_config = {
            'username': 'beihai',
            'password': 'beihai',
        }
        for _ in xrange(3):

            try:
                r = requests.post(proxy_url, json=user_config, timeout=10)
                if r.status_code != 200:
                    continue
                json_data = json.loads(r.text)
                is_success = json_data.get('success')
                if not is_success:
                    continue

                proxy = json_data.get('proxy')
                if proxy is None:
                    continue
                log.info("当前获取的代理: proxy = {}".format(proxy))
                return {'http': proxy}
            except Exception as e:
                log.error("获取代理失败:")
                log.exception(e)

        return None
