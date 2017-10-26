#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time: 2017/9/22 下午3:15
@Author: CZC
@File: 171_106_48_55.py
"""
import random
import sys

import requests

sys.path.append('../')
sys.path.append('../..')
sys.path.append('../../..')
from sites.common import util, staticproxy

from libs.thrift_utils.thrift_object_generator import gen_download_rsp
from libs.thrift_utils.thrift_serialize import thriftobj2bytes
from conf import m_settings
from libs.taskbase import TaskBase
from libs.loghandler import getLogger


BASE_URL = 'http://171.106.48.55:8899/legalsystem/ReportServer?reportlet=ktgg/ktgglist.cpt&fbdm=450000'
MAX_RETRY = 5
TIMEOUT = 60
PAGES = 400

class GxCourt(TaskBase):
    def __init__(self):
        super(GxCourt, self).__init__()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.session = None
        self.session_id = None
        self.url = 'http://171.106.48.55:8899/legalsystem/ReportServer?&op=page_content&sessionID={sessionID}&pn={pn}'

    def start(self):
        self.session_id = self.get_session_id()
        for pn in xrange(PAGES):
            pn += 1
            url = self.url.format(sessionID=self.session_id, pn=pn)
            response = self.requester(url, max_retry=MAX_RETRY, timeout=TIMEOUT)
            self.check_session(response)
            self.logger.info(response.url)
            self.put_bean(url, response)

    def get_session_id(self):
        self.session = requests.session()
        response = self.requester(BASE_URL, max_retry=MAX_RETRY, timeout=TIMEOUT)
        if response is None:
            self.logger.warning('获取session失败，正在重试……')
            return self.get_session_id()
        session_id = util.get_match_value("register\('", "'", response.content)

        session_id = int(session_id)
        return session_id

    def check_session(self, response):
        if 'Session Timeout...' in response:
            self.logger.info('由于当前Session的超时, 或者超过了允许的并发用户数, 产生Session过期, 正在重新获取sessionID')
            self.session_id = self.get_session_id()

    @staticmethod
    def get_proxy():
        all_ip = staticproxy.get_all_proxie()
        if not isinstance(all_ip, list) or len(all_ip) <= 0:
            raise Exception('代理初始化异常……')
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        # logger.info("更换ip为:{}".format(ip))
        return ip

    def requester(self, url, data=None, params=None, max_retry=3, timeout=60):
        self.session.proxies = self.get_proxy()
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            if try_count >= max_retry / 2:
                self.session.proxies = self.get_proxy()  # 更换代理
            try:
                if not data:
                    response = self.session.get(url, params=params, timeout=timeout)
                else:
                    response = self.session.post(url, data=data, params=params, timeout=timeout)
                if response.status_code == 200 and response is not None:
                    return response

            except Exception as e:
                self.logger.error("访问 {}出现未知的错误".format(url))
                self.logger.exception(e)
            self.logger.error("第{}次重试访问 {}页面失败".format(try_count, url))
        return

    def put_bean(self, url, response):
        try:
            obj = gen_download_rsp(url, response.content)
            beanstalk_client = m_settings.beanstalk_client2()
            output_tube = m_settings.BEANSTALKD_TUBE.get('download_rsp')
            beanstalk_client.put(output_tube, thriftobj2bytes(obj))
        except Exception as e:
            self.logger.error(e)


if __name__ == "__main__":
    worker = GxCourt()
    worker()
