#!/usr/bin/env python
# encoding: utf-8
import random

import requests
import time

static_proxy_url="http://112.74.163.187:23128/__static__/proxies.txt"
def get_all_proxie():
    try_times = 0

    while try_times <= 3:
        try_times += 1
        try:
            proxy_list = []
            r = requests.get(static_proxy_url, timeout=10)
            if r is None or r.status_code != 200:
                continue
            line_list = r.text.split("\n")
            for line in line_list:
                line = line.strip("\r").strip("\n").strip()
                # if '7777' in line:
                #     line = line.replace('7777', '55555')
                # elif '8088' in line:
                #     line = line.replace('8088', '1088')

                if len(line) <= 0:
                    continue

                proxies = {'http': 'http://{}'.format(line), 'https': 'http://{}'.format(line)}
                proxy_list.append(proxies)
            return proxy_list
        except Exception:
            time.sleep(5)
            pass

    raise Exception('重试获取代理失败...')

def get_phantom_proxy():
    try_times = 0

    while try_times <= 3:
        try_times += 1
        try:
            proxy_list = []
            r = requests.get(static_proxy_url, timeout=10)
            if r is None or r.status_code != 200:
                continue
            line_list = r.text.split("\n")
            for line in line_list:
                line = line.strip("\r").strip("\n").strip()
                # if '7777' in line:
                #     line = line.replace('7777', '55555')
                # elif '8088' in line:
                #     line = line.replace('8088', '1088')

                if len(line) <= 0:
                    continue

                proxies = {'http': 'http://{}'.format(line)}
                proxy_list.append(proxies)
            return proxy_list
        except Exception:
            time.sleep(5)
            pass

    raise Exception('重试获取代理失败...')


if __name__ == "__main__":
    all_ip = get_all_proxie()
    pass
