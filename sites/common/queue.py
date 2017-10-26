#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/17'

import redis
import json
from page import Page as page

class Queue(object):

    def __init__(self,queueName):
        self.queueName="redis_queue_list_"+queueName
        self.mapName = "redis_queue_map_"+queueName
        self.redis= redis.Redis(host='172.18.180.224', port=6379,password="haizhi@)")

    def push(self,url):
        if self.redis.hget(self.mapName,url) is None:
            self.redis.hset(self.mapName,url,url)
            self.redis.rpush(self.queueName,url)

    def poll(self):
        while True:
            dataKey = self.redis.lpop(self.queueName)
            if dataKey is not None:
                value = self.redis.hget(self.mapName, dataKey)
                if value is not None:
                    return dataKey,value
                else:
                    continue
            else:
                return "",""

    def clean(self):
        self.redis.delete(self.queueName)
        self.redis.delete(self.mapName)

    def ack(self,url):
        self.redis.hdel(self.mapName,url)

    def repair(self):
        cursor = '0'
        while cursor != 0:
            cursor, data = self.redis.hscan(self.mapName, cursor=cursor)
            for item in data.items():
                url=item[0]
                self.redis.rpush(self.queueName,url)

    def size(self):
        return self.redis.hlen(self.mapName)


if __name__ == "__main__":
    queue = Queue("supreme_court_detail_test")
    #queue.repair()
    page={}
    url="http://wenshu.court.gov.cn/wenshu_court_gov_cn_list/wenshu_court_gov_cn_list/?sorttype=1&co"
    page["method"] ="get"
    queue.push(page)
    while True:
        result=queue.poll()
        if result is not None:
            print  result
        else:
            break
