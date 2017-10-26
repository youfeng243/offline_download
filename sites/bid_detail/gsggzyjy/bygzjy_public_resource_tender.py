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

import urlutils

from conf import m_settings
from libs.fetcher import Fetcher
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
import parser_content
import re
# from pyquery import PyQuery as py, PyQuery
from sectionSeed import SectionSeed as ssd

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


class BygzjyPublicResourceTenderWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "白银"

    def extract_detail_link(self, srcUrl, response):
        html = response.text
        dataHtml = html.split(",")[0]
        bsoup = BeautifulSoup(dataHtml)
        titleElements = bsoup.select("a[class=infolist_a]")
        publishDateElements = bsoup.select('span[class=infolist_date]')
        size = len(titleElements)
        for i in range(0, size):
            titleElement = titleElements[i]
            title = titleElement.attrs["title"]
            url = titleElement.attrs["href"]
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
        filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
        data = self.fetcher.download_file(pdf_link, filename=filename)
        data['sourceUrl'] = response.url
        data['title'] = title
        data['publish_time'] = publish_time
        extract_data = parser_content.deal(data)
        if extract_data:
            extract_data['province'] = self.province
            extract_data['city'] = self.city
            self.sendData(data, extract_data)

    def buildData(self, filename, length, data, url):
        return {"filename": filename, "length": length, "data": data, "sourceUrl": url}

    def sendData(self, data, extract_data):
        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                     extract_data)))

    def printData(self, data, content):
        self.resultCount += 1
        print "index" + str(self.resultCount)
        print "title:" + data["title"]
        print "publishTime:" + data["publish_time"]
        print "content:"
        print content["content"]

    def start(self):
        self.logger.info("开始执行: BygzjyPublicResourceTenderWorker")
        sectionSeeds = []

        buildTender = ssd("市政、房建工程", "http://www.bygzjy.cn/InfoPage/InfoListInfo.aspx?SiteItem=4TE8hgQqkCk%3D",
                          "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx",
                          "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx", 26)
        sectionSeeds.append(buildTender)

        gvPurchase = ssd("政府采购", "http://www.bygzjy.cn/InfoPage/InfoListInfo.aspx?SiteItem=fVoViMwBm04%3D",
                         "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx",
                         "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx", 27)
        sectionSeeds.append(gvPurchase)

        resourcesTransaction = ssd("国土、矿权、产权交易",
                                   "http://www.bygzjy.cn/InfoPage/InfoListInfo.aspx?SiteItem=tyyTkKXO4D4%3D",
                                   "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx",
                                   "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx", 28)
        sectionSeeds.append(resourcesTransaction)

        trafficWaterConservancyTender = ssd("交通、水利工程",
                                            "http://www.bygzjy.cn/InfoPage/InfoListInfo.aspx?SiteItem=wNfZJUVZ7Y4%3D",
                                            "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx",
                                            "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx", 29)
        sectionSeeds.append(trafficWaterConservancyTender)

        medicalApparatus = ssd("医疗器械", "http://www.bygzjy.cn/InfoPage/InfoListInfo.aspx?SiteItem=zJlkEDhqgOY%3D",
                               "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx",
                               "http://www.bygzjy.cn/Handlers/InfoPageTrade.ashx", 31)
        sectionSeeds.append(medicalApparatus)

        pageSize = 30
        for sectionSeed in sectionSeeds:
            try:
                self.fetcher.get(sectionSeed.initUrl)
                totalPageCount = self.getTotalPageCount(pageSize, sectionSeed.getTotalPageUrl, sectionSeed.siteItem)
                if totalPageCount < 1:
                    return
                for pageIndex in xrange(1, totalPageCount + 1):
                    data = self.getPostData(pageIndex, pageSize, sectionSeed.siteItem)
                    response = self.fetcher.post(sectionSeed.getDataUrl, data=data)
                    self.extract_detail_link(sectionSeed.initUrl, response)
            except Exception as e:
                self.logger.exception(e)
        self.logger.info("执行完成: BygzjyPublicResourceTenderWorker")

    def getTotalPageCount(self, pageSize, getTotalPageUrl, siteItem):
        """
        获取列表页分页总数
        Returns: 分页总数
        """
        dataMap = self.getPostData(1, pageSize, siteItem)
        response = self.fetcher.post(getTotalPageUrl, data=dataMap)
        content = response.content
        pageCount = int(content.split(",")[1])
        tempNum = pageCount % pageSize
        pageCount = pageCount / pageSize
        if tempNum != 0:
            pageCount = pageCount + 1
        return pageCount

    def getPostData(self, pageIndex, pageSize, siteItem):
        dataMap = {}
        dataMap["pageIndex"] = pageIndex
        dataMap["pageSize"] = pageSize
        dataMap["siteItem"] = siteItem
        dataMap["infoType"] = ""
        dataMap["query"] = ""
        return dataMap


if __name__ == "__main__":
    worker = BygzjyPublicResourceTenderWorker()
    worker()
