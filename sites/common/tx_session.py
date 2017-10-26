#!/usr/bin/env python
# coding:utf-8
import json

import requests

from conf.m_settings import log

__author__ = 'clevertang'

from requests import Session

from libs.loghandler import getLogger

logger = getLogger()

default_retry = 3
default_timeout = 10


def get_proxy():
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


class proxy_session(Session):
    # TODO 加一些钩子做请求统计
    def get(self, url, **kwargs):
        try_cnt = 0
        max_try = kwargs.get("retry", default_retry)
        last_error = None
        if not kwargs.get("timeout"):
            kwargs['timeout'] = default_timeout
        if not kwargs.get("proxies"):
            kwargs['proxies'] = get_proxy()
        while try_cnt < max_try:
            try:
                try_cnt += 1
                resp = self.request("GET", url, **kwargs)
                if resp is not None and resp.status_code == 200:
                    logger.info("GET-SUCCESS:{}\t{}".format(url, resp.status_code))
                    return resp
            except Exception as e:
                kwargs['proxies'] = get_proxy()
                last_error = e
        if try_cnt >= max_try:
            return
        raise last_error

    # TODO 加一些钩子做请求统计
    def post(self, url, data=None, json=None, **kwargs):
        try_cnt = 0
        max_try = kwargs.get("retry", default_retry)
        last_error = None
        if not kwargs.get("timeout"):
            kwargs['timeout'] = default_timeout
        if not kwargs.get("proxies"):
            kwargs['proxies'] = get_proxy()
        while try_cnt < max_try:
            try:
                try_cnt += 1
                resp = self.request("POST", url, data=data, json=json, **kwargs)
                if resp is not None and resp.status_code == 200:
                    logger.info("POST-SUCCESS:{}\t{}".format(url, resp.status_code))
                    return resp
            except Exception as e:
                kwargs['proxies'] = get_proxy()
                last_error = e
                logger.warn("POST-FAILED:{}\ttry:\t{}".format(url, try_cnt, e.message))
        if try_cnt >= max_try:
            return
        raise last_error
