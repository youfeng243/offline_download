#!/usr/bin/env python
# coding:utf-8
import random

from sites.common.staticproxy import get_all_proxie

__author__ = 'clevertang'

from requests import Session

from libs.loghandler import getLogger

logger = getLogger()

default_retry = 3
default_timeout = 10

all_ip = get_all_proxie()


def get_proxy():
    ip = all_ip[random.randint(0, len(all_ip) - 1)]
    logger.info("更换ip为:{}".format(ip))
    return ip


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
