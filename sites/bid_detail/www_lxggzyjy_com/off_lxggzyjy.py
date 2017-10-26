#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.bid_detail.common import parser_content
from sites.bid_detail.common import urlutils
from sites.bid_detail.common.sectionSeed import SectionSeed

from conf import m_settings
from libs.fetcher import Fetcher
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from libs.taskbase import TaskBase
from libs.loghandler import getLogger

import re
from pyquery import PyQuery
from bs4 import BeautifulSoup


post_data = {

}
detail_link_regx = re.compile("""href='\s*(cpwsplay.*?)'""")
detail_title_regx = re.compile("""href='\s*cpwsplay.*?>(.*?)</a>""")
pdf_link_regx = re.compile('<iframe.*?src="(.*?)"')
title_regx = re.compile('<div.*?title.*>(.*?)</div>')

headMap = {}
headMap["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
headMap["Accept-Language"] = "zh-CN,zh;q=0.8"
headMap["Cache-Control"] = "max-age=0"
headMap[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
headMap["Upgrade-Insecure-Requests"] = "1"


class LxggzyjyCrawler(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "临夏"

    def extract_detail_link(self, srcUrl, response):
        html = response.content
        startFlag = "<ul>"
        endFlag = "</ul>"
        startIndex = html.index(startFlag)
        endIndex = html.index(endFlag)
        html = html[startIndex:endIndex + len(endFlag)]

        bsoup = BeautifulSoup(html)
        titleElements = bsoup.select("a")
        publishDateElements = bsoup.select('span')
        size = len(titleElements)
        for i in range(0, size):
            titleElement = titleElements[i]
            url = titleElement.attrs["href"]
            title = titleElement.attrs["title"]
            publishDate = publishDateElements[i].get_text()
            if "" != url:
                newUrl = urlutils.assembleUrl(srcUrl, url)
                # self.fetcher.async_get(url="http://www.gsggzyjy.cn" + url, callback=self.extract_pdf_link)
                response = self.fetcher.get(newUrl)
                self.extract_pdf_link(response, title, publishDate)

    def extract_pdf_link(self, response, title, publish_time):

        iframeSelects = []
        iframeSelects.append("iframe[id=Iframe]")
        iframeSelects.append("iframe[id=viewIframe2]")

        parser = PyQuery(response.content, parser='html')
        pdfLinkFlag = "file="
        pdfFlag = ".pdf"
        pdf_link = ''
        filename = ''
        data = None
        extract_data = None
        try:
            for iframeSelect in iframeSelects:
                pdf_link = parser.find(iframeSelect).attr('src')
                if pdf_link is not None and "" != pdf_link:
                    startIndex = pdf_link.find(pdfLinkFlag)
                    if startIndex >= 0:
                        pdf_link = pdf_link[startIndex + len(pdfLinkFlag):len(pdf_link)]
                        endIndex = pdf_link.rfind(pdfFlag)
                        pdf_link = pdf_link[0:endIndex + len(pdfFlag)]
                    break
        except Exception, e:
            pass
        if pdf_link is not None and "" != pdf_link:
            filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
            data = self.fetcher.download_file(pdf_link, filename=filename)
            data['sourceUrl'] = response.url
            data['title'] = title
            data['publish_time'] = publish_time
            extract_data = parser_content.deal(data)
        else:
            content = parser.find("div[class=infocnt]").text()
            data = self.buildData(title, len(content), content, response.url)
            data['title'] = title
            data['publish_time'] = publish_time
            extract_data = parser_content.dealTakeText(data, content)
        if extract_data:
            extract_data['province'] = self.province
            extract_data['city'] = self.city
            self.sendData(data, extract_data)
            # self.printData(title, publish_time, extract_data["content"])

    def buildData(self, filename, length, data, url):
        return {"filename": filename, "length": length, "data": data, "sourceUrl": url}

    def sendData(self, data, extract_data):
        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                     extract_data)))

    def printData(self, title, publishTime, content):
        self.resultCount = self.resultCount + 1
        print "index" + str(self.resultCount)
        print "title:" + title
        print "publishTime:" + publishTime
        print "content:"
        print  content

    def start(self):

        self.logger.info("开始执行: LxggzyjyCrawler")

        sectionSeeds = []

        ajaxUrl = None
        ajaxUrlFlag = "{ajaxUrl}"

        buildTender = SectionSeed("建设工程", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=31",
                          "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                          "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(buildTender)

        gvPurchase = SectionSeed("政府采购", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=33",
                         "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                         "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(gvPurchase)

        trafficTender = SectionSeed("交通项目", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=39",
                            "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                            "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(trafficTender)

        waterConservancyTender = SectionSeed("水利项目", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=62",
                                     "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                                     "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(waterConservancyTender)

        comprehensiveTender = SectionSeed("综合项目", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=81",
                                  "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                                  "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(comprehensiveTender)

        resourcesTransaction = SectionSeed("国土、矿权、产权交易", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=35",
                                   "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                                   "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(resourcesTransaction)

        landTender = SectionSeed("国土项目", "http://www.lxggzyjy.com/InfoPage/InfoList.aspx?SiteItemID=80",
                         "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getTotalPages&_session=rw",
                         "http://www.lxggzyjy.com" + ajaxUrlFlag + "?_method=getCurrentData&_session=rw")
        sectionSeeds.append(landTender)

        for sectionSeed in sectionSeeds:
            try:
                initRespone = self.fetcher.get(sectionSeed.initUrl)
                ajaxUrl = self.getAjaxUrl(initRespone)
                getTotalPageUrl = sectionSeed.getTotalPageUrl.replace(ajaxUrlFlag, ajaxUrl)
                totalPageCount = int(self.getTotalPageCount(getTotalPageUrl))
                if totalPageCount < 1:
                    return
                for pageIndex in xrange(1, totalPageCount + 1):
                    data = "Query=\ncurrentPage=" + str(pageIndex)
                    getDataUrl = sectionSeed.getDataUrl.replace(ajaxUrlFlag, ajaxUrl)
                    response = self.fetcher.post(getDataUrl, data=data)
                    self.extract_detail_link(sectionSeed.initUrl, response)
            except Exception as e:
                self.logger.exception(e)
        self.logger.info("执行完成: LxggzyjyCrawler")

    def getAjaxUrl(self, initRespone):
        result = None
        parser = BeautifulSoup(initRespone.content)
        scripts = parser.select("script")
        for script in scripts:
            src = None
            try:
                src = script.attrs["src"]
            except Exception, e:
                pass
            if src is not None and src.find("/ajax/Controls_InfoList") != -1:
                result = src
                break
        return result

    def getTotalPageCount(self, getTotalPageUrl):
        """
        获取列表页分页总数
        Returns: 分页总数
        """
        data = "Query="
        response = self.fetcher.post(getTotalPageUrl, data=data)
        totalPageCount = response.content
        return totalPageCount


if __name__ == "__main__":
    worker = LxggzyjyCrawler()
    worker()
