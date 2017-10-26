#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time: 2017/8/28 下午3:15
@Author: CZC
@File: 171_106_48_55.py
"""

import sys
sys.path.append('../')
sys.path.append('../..')
sys.path.append('../../..')
from sites.common.requests_with_proxy import requester
from sites.common import util

from libs.thrift_utils.thrift_object_generator import gen_download_req
from libs.thrift_utils.thrift_serialize import thriftobj2bytes
from conf import m_settings
from libs.taskbase import TaskBase
from libs.loghandler import getLogger


BASE_URL = 'http://171.106.48.55:28040/List/ListContent'
MAX_RETRY = 5
TIMEOUT = 60


class GxCourt(TaskBase):
    def __init__(self):
        super(GxCourt, self).__init__()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.post_data = {
            'Index': '1',
            'Page': '20',
            'Order': '裁判日期',
            'Direction': 'desc',
            'Param': '',
        }

    def start(self):
        pages = self.get_pages()
        for index in xrange(pages):
            self.post_data['Index'] = str(int(index) + 1)
            d = len(self.post_data)
            self.put_bean(BASE_URL)

    def get_pages(self):
        response = requester(BASE_URL, data=self.post_data, max_retry=MAX_RETRY, timeout=TIMEOUT)
        if response is None:
            self.logger.warning('获取页数失败，正在重试……')
            return self.get_pages()
        content = response.content
        json_content = util.json_loads(content)
        counts = util.get_match_value('"Count":"', '"', json_content, True)

        counts = int(counts[0])
        per_page_counts = self.post_data.get('Page', 20)
        pages = (counts/int(per_page_counts)) + 1
        return pages

    def put_bean(self, url):
        try:
            self.logger.info(url, self.post_data.get('Index'))
            obj = gen_download_req(url, method='post', post_data=self.post_data)
            beanstalk_client = m_settings.beanstalk_client2()
            output_tube = m_settings.BEANSTALKD_TUBE.get('download_req')
            beanstalk_client.put(output_tube, thriftobj2bytes(obj))
        except Exception as e:
            self.logger.error(e)


if __name__ == "__main__":
    worker = GxCourt()
    worker()
