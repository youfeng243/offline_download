#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-22 18:54
import json
import os

import requests

from conf import m_settings
from libs.loghandler import getLogger

class ProxyHandler():
    def __init__(self, key):
        self.key = key

    def get_proxy(self):
        result = json.loads(requests.get(
            url='%s/api/download/get_proxy?site=%s' % (settings.PROXY_HOST, self.key)).text).get("proxy")
        type, info = result.split("://")
        return {type:"http://"+info}

    def report_proxy(self, proxy, status = False):
        pass

