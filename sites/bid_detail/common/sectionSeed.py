#!/usr/bin/env python
# -*- coding:utf-8 -*-

class SectionSeed(object):

    def __init__(self, section, initUrl, getTotalPageUrl, getDataUrl,siteItem=None):
        self.section = section
        self.initUrl = initUrl
        self.getTotalPageUrl = getTotalPageUrl
        self.getDataUrl = getDataUrl
        self.siteItem=siteItem
