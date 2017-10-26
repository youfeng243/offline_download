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


class GnggzyjyCrawler(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "甘南"

    def extract_detail_link(self, srcUrl, response):
        html = response.content
        bsoup = BeautifulSoup(html)
        titleElements = bsoup.select("div ul li a")
        publishDateElements = bsoup.select('div ul li a i')
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

    def buildData(self, filename, length, data, url):
        return {"filename": filename, "length": length, "data": data, "sourceUrl": url}

    def sendData(self, data, extract_data):
        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                     extract_data)))

    def printData(self, data, content):
        self.resultCount = self.resultCount + 1
        print "index" + str(self.resultCount)
        print "title:" + data["title"]
        print "publishTime:" + data["publish_time"]
        print "content:"
        print  content["content"]

    def start(self):
        self.logger.info("开始执行: GnggzyjyCrawler")
        sectionSeeds = []

        # buildTender = ssd("建设工程", "http://www.gnggzyjy.com/InfoPage/InfoList.aspx?SiteItem=22",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=22&page=1&query=",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=22&page={pageIndex}&query=")
        # sectionSeeds.append(buildTender)
        #
        # gvPurchase = ssd("政府采购", "http://www.gnggzyjy.com/InfoPage/InfoList.aspx?SiteItem=25",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=25&page=1&query=",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=25&page={pageIndex}&query=")
        # sectionSeeds.append(gvPurchase)
        #
        # medicalTender = ssd("药品及医疗器械", "http://www.gnggzyjy.com/InfoPage/InfoList.aspx?SiteItem=27",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=27&page=1&query=",
        #                   "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=27&page={pageIndex}&query=")
        # sectionSeeds.append(medicalTender)

        resourcesTransaction = SectionSeed("土地及产权交易", "http://www.gnggzyjy.com/InfoPage/InfoList.aspx?SiteItem=29",
                                           "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=29&page=1&query=",
                                           "http://www.gnggzyjy.com/InfoPage/InfoListInfo.aspx?SiteItem=29&page={pageIndex}&query=")
        sectionSeeds.append(resourcesTransaction)

        for sectionSeed in sectionSeeds:
            try:
                self.fetcher.get(sectionSeed.initUrl)
                totalPageCount = int(self.getTotalPageCount(sectionSeed.getTotalPageUrl))
                if totalPageCount < 1:
                    return
                for pageIndex in xrange(1, totalPageCount + 1):
                    url = sectionSeed.getDataUrl.replace("{pageIndex}", str(pageIndex))
                    response = self.fetcher.get(url)
                    self.extract_detail_link(sectionSeed.initUrl, response)
            except Exception as e:
                self.logger.exception(e)
        self.logger.info("执行完成: GnggzyjyCrawler")

    def getTotalPageCount(self, getTotalPageUrl):
        """
        获取列表页分页总数
        Returns: 分页总数
        """
        response = self.fetcher.get(getTotalPageUrl)
        parser = PyQuery(response.content, parser='html')
        totalPageCount = parser.find("span[id=labPageCount]").text()
        return totalPageCount


if __name__ == "__main__":
    worker = GnggzyjyCrawler()
    worker()
