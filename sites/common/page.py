#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'


class Page(object):

    def __init__(self,url,method="get",referer=None,postDataMap=None):
        self.url=url
        self.method = method
        self.referer = referer
        self.postDataMap = postDataMap
        self.content=""
        self.retryCount= 0