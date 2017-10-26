#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
import sys

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
from pyquery import PyQuery as py
from sectionSeed import SectionSeed  as ssd

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


class LanzhouPublicResourceTenderWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "兰州"

    def extract_detail_link(self, srcUrl, response):
        startFlag = "<ul>"
        endFlag = "</ul>"
        html = response.content
        startIndex = html.index(startFlag)
        endIndex = html.index(endFlag)
        html = html[startIndex:endIndex + len(endFlag)]
        pyq = py(html, parser='html')
        for i in range(0, len(pyq.find('a'))):
            url = pyq.find('a').eq(i).attr('href')
            if "" != url:
                newUrl = urlutils.assembleUrl(srcUrl, url)
                # self.fetcher.async_get(url="http://www.gsggzyjy.cn" + url, callback=self.extract_pdf_link)
                response = self.fetcher.get(newUrl)
                self.extract_pdf_link(response)

    def extract_pdf_link(self, response):
        titleSelect = "div[class=content]>div[class=txt-download]>div[class=texts-up]>h2"
        # div[class=content]>div[class=texts]>div[class=texts-up]>h2

        iframeSelects = []
        iframeSelects.append("iframe[id=Iframe]")
        iframeSelects.append("iframe[id=viewIframe2]")

        titleSelects = []
        titleSelects.append("div[class=content]>div[class=txt-download]>div[class=texts-up]>h2")
        titleSelects.append("div[class=content]>div[class=texts]>div[class=texts-up]>h2")

        publishTimeSelects = []
        publishTimeSelects.append("div[class=content]>div[class=txt-download]>div[class=texts-up]>p:contains(发布时间)")
        publishTimeSelects.append("div[class=content]>div[class=texts]>div[class=texts-up]>p:contains(发布时间)")

        cententSelect = "div[class=content]>div[class=texts]>div[class=texts-down]"

        # pdf_link = str(response.content).split('下载公告PDF文件')[0].split('href="')[-1].split('"')[0]
        # filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
        parser = py(response.content, parser='html')
        pdfLinkFlag = "file="
        pdfFlag = ".pdf"
        pdf_link = ''
        filename = ''
        title = ''
        publish_time = ''
        data = None
        extract_data = None
        try:
            for iframeSelect in iframeSelects:
                iframeSrc = parser.find(iframeSelect).attr('src')
                if iframeSrc is not None and "" != iframeSrc:
                    startIndex = iframeSrc.find(pdfLinkFlag)
                    if startIndex >= 0:
                        pdf_link = iframeSrc[startIndex + len(pdfLinkFlag):len(iframeSrc)]
                        endIndex = pdf_link.rfind(pdfFlag)
                        pdf_link = pdf_link[0:endIndex + len(pdfFlag)]
                        filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
                    break

            for titleSelect in titleSelects:
                title = parser.find(titleSelect).text()
                if "" != title:
                    break
            for publishTimeSelect in publishTimeSelects:
                publish_time = parser.find(publishTimeSelect).text()
                if "" != publish_time:
                    publish_time = publish_time.replace("发布时间：", "")
                    publish_time = publish_time.replace("发布时间:", "")
                    break
        except Exception as e:
            self.logger.exception(e)

        if "" != pdf_link:
            data = self.fetcher.download_file(pdf_link, filename=filename)
            data['sourceUrl'] = response.url
            data['title'] = title
            data['publish_time'] = publish_time
            extract_data = parser_content.deal(data)
        else:
            content = parser.find(cententSelect).text()
            data = self.buildData(title, len(content), content, response.url)
            data['title'] = title
            data['publish_time'] = publish_time
            extract_data = parser_content.dealTakeText(data, content)
        if extract_data:
            extract_data['province'] = self.province
            extract_data['city'] = self.city
            self.sendData(data, extract_data)
            # self.printData(title,publish_time,extract_data["content"])

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
        self.logger.info("开始执行: LanzhouPublicResourceTenderWorker")
        sectionSeeds = []

        buildTender = ssd("建设工程", "http://www.lzggzyjy.cn/InfoPage/InfoList.aspx?SiteItem=36",
                          "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_c5g3rkaa.ashx?_method=getTotalPages&_session=rw",
                          "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_c5g3rkaa.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(buildTender)

        gvPurchase = ssd("政府采购", "http://www.lzggzyjy.cn/InfoPage/InfoList.aspx?SiteItem=40",
                         "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getTotalPages&_session=rw",
                         "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(gvPurchase)

        resourcesTransaction = ssd("国土、矿权、产权交易", "http://www.lzggzyjy.cn/InfoPage/InfoList.aspx?SiteItem=46",
                                   "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getTotalPages&_session=rw",
                                   "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(resourcesTransaction)

        otherTransaction = ssd("其他交易", "http://www.lzggzyjy.cn/InfoPage/InfoList.aspx?SiteItem=49",
                               "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getTotalPages&_session=rw",
                               "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(otherTransaction)

        countyTender = ssd("区县项目招标", "http://www.lzggzyjy.cn/InfoPage/InfoList.aspx?SiteItem=52",
                           "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getTotalPages&_session=rw",
                           "http://www.lzggzyjy.cn/ajax/Controls_InfoListControl,App_Web_qumnj53o.ashx?_method=getCurrentData&_session=rw")
        sectionSeeds.append(countyTender)

        for sectionSeed in sectionSeeds:
            try:
                self.fetcher.get(sectionSeed.initUrl)
                totalPageCount = int(self.getTotalPageCount(sectionSeed.getTotalPageUrl))
                if totalPageCount < 1:
                    return
                for pageIndex in xrange(1, totalPageCount + 1):
                    data = "Query=\ncurrentPage=" + str(pageIndex)
                    response = self.fetcher.post(sectionSeed.getDataUrl, data=data)
                    self.extract_detail_link(sectionSeed.initUrl, response)
            except Exception as e:
                self.logger.exception(e)

        self.logger.info("执行完成: LanzhouPublicResourceTenderWorker")

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
    worker = LanzhouPublicResourceTenderWorker()
    worker()
