#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-18 11:54

from libs.fetcher import Fetcher

def func():
    for x in []:
        yield x
    return

print func()
fc = Fetcher()
fc.donwload("http://fy.jimei.gov.cn/sfgk/tsgk/ktgg/201612/P020161214364660071043.doc")