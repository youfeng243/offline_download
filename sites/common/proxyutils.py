#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
# http://112.74.163.187:23128/__static__/proxies.txt

import requests

remote_proxy_conf = {
    'host': '172.18.180.225',
    'port': 9300,
}


def getProxy(requestHost):
    proxies = None
    ssl_type = "http"
    try:
        host_url = 'http://{host}:{port}/proxy/{h}'.format(h=requestHost, host=remote_proxy_conf['host'],
                                                           port=remote_proxy_conf['port'])
        r = requests.get(host_url, timeout=3)
        if r is None or r.status_code != 200 or 'failed' in r.text or 'False' in r.text:
            pass
        else:
            value='http://{host}'.format(host=r.text)
            proxies = {ssl_type: value}
    except Exception as e:
        pass
    return proxies


if __name__ == "__main__":
    proxy = getProxy("wenshu.court.gov.cn")
    print proxy
