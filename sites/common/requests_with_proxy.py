#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time: 2017/8/29 下午4:12
@Author: CZC
@File: requests_with_proxy.py
"""
import random
import requests
import staticproxy
from libs.loghandler import getLogger

logger = getLogger(__name__, console_out=False, level="debug")


# todo 目前自用中，后续不断完善
def get_proxy():
        all_ip = staticproxy.get_all_proxie()
        if not isinstance(all_ip, list) or len(all_ip) <= 0:
            raise Exception('代理初始化异常……')
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        # logger.info("更换ip为:{}".format(ip))
        return ip


def requester(url, data=None, params=None, max_retry=3, timeout=60):
    session = requests.session()
    session.proxies = get_proxy()
    try_count = 0
    while try_count < max_retry:
        try_count += 1
        if try_count >= max_retry/2:
            session.proxies = get_proxy()  # 更换代理
        try:
            if not data:
                response = session.get(url, params=params, timeout=timeout)
            else:
                response = session.post(url, data=data, params=params, timeout=timeout)
            if response.status_code == 200 and response is not None:
                return response

        except Exception as e:
            logger.error("访问 {}出现未知的错误".format(url))
            logger.exception(e)
        logger.error("第{}次重试访问 {}页面失败".format(try_count, url))
    return
