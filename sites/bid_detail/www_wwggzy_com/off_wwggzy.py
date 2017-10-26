#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
import sys

from bs4 import BeautifulSoup
from pyquery import PyQuery

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


class WwggzyCrawler(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "武威市"

    def extract_detail_link(self, srcUrl, response):
        html = response.content
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
        except Exception as e:
            self.logger.exception(e)
        if pdf_link is not None and "" != pdf_link:
            filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
            data = self.fetcher.download_file(pdf_link, filename=filename)
            data['sourceUrl'] = response.url
            data['title'] = title
            data['publish_time'] = publish_time
            extract_data = parser_content.deal(data)
        else:
            content = parser.find("div[class=main_con_sub2_con]").text()
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
        self.resultCount += 1
        print "index" + str(self.resultCount)
        print "title:" + title
        print "publishTime:" + publishTime
        print "content:"
        print content

    def start(self):

        self.logger.info("开始执行: WwggzyCrawler")
        sectionSeeds = []

        buildTender = SectionSeed("建设工程", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=29",
                                  "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                  "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(buildTender)

        trafficTender = SectionSeed("交通工程", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=37",
                                    "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                    "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(trafficTender)

        waterConservancyTender = SectionSeed("水利工程", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=42",
                                             "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                             "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(waterConservancyTender)

        gvPurchase = SectionSeed("政府采购", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=48",
                                 "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                 "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(gvPurchase)

        propertyTender = SectionSeed("产权交易", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=56",
                                     "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                     "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(propertyTender)

        landTender = SectionSeed("土地整理", "http://www.wwggzy.com/InfoPage/InfoList.aspx?SiteItem=59",
                                 "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getTotalPages&_session=rw",
                                 "http://www.wwggzy.com/ajax/Controls_InfoListControl,App_Web_m1c2wyi1.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(landTender)

        for sectionSeed in sectionSeeds:
            try:
                self.fetcher.get(sectionSeed.initUrl)
                totalPageCount = self.getTotalPageCount(sectionSeed.getTotalPageUrl)
                if totalPageCount < 1:
                    return
                for pageIndex in xrange(1, totalPageCount + 1):
                    data = "Query=\ncurrentPage=" + str(pageIndex)
                    response = self.fetcher.post(sectionSeed.getDataUrl, data=data)
                    self.extract_detail_link(sectionSeed.initUrl, response)
            except Exception as e:
                self.logger.exception(e)

        self.logger.info("执行完成: WwggzyCrawler")

    def getTotalPageCount(self, getTotalPageUrl):
        """
        获取列表页分页总数
        Returns: 分页总数
        """
        data = "Query="
        response = self.fetcher.post(getTotalPageUrl, data=data)
        content = response.content
        return int(content)

    def getPostData(self, pageIndex, pageSize, siteItem):
        dataMap = {}
        dataMap["pageIndex"] = pageIndex
        dataMap["pageSize"] = pageSize
        dataMap["siteItem"] = siteItem
        dataMap["infoType"] = ""
        dataMap["query"] = ""
        return dataMap


if __name__ == "__main__":
    worker = WwggzyCrawler()
    worker()
