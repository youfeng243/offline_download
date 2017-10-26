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
from pyquery import PyQuery
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


class LnsggzyjyPublicResourceTenderWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.province = "甘肃省"
        self.city = "陇南"
        self.logger.info("初始化完成: LnsggzyjyPublicResourceTenderWorker")

    def extract_detail_link(self, srcUrl, response):
        html = response.content
        parser = PyQuery(html, parser='html')
        titleElements = parser.find("table[id=MoreInfoList1_DataGrid1]>tr>td>a")
        publishDateElements = parser.find('table[id=MoreInfoList1_DataGrid1]>tr>td:eq(2)')
        size = len(titleElements)
        for i in range(0, size):
            titleElement = titleElements.eq(i)
            url = titleElement.attr("href")
            title = titleElement.attr("title")
            publishDate = publishDateElements.eq(i).text()
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
            content = parser.find("td[id=TDContent]").text()
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

    def printData(self, data, content):
        self.resultCount = self.resultCount + 1
        print "index" + str(self.resultCount)
        print "title:" + data["title"]
        print "publishTime:" + data["publish_time"]
        print "content:"
        print  content

    def start(self):
        sectionSeeds = []

        buildTender = ssd("房建及市政",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004001/004001001/MoreInfo.aspx?CategoryNum=004001001",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004001/004001001/MoreInfo.aspx?CategoryNum=004001001",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004001/004001001/MoreInfo.aspx?CategoryNum=004001001")
        sectionSeeds.append(buildTender)

        waterConservancyTender = ssd(" 水利项目",
                                     "http://www.lnsggzyjy.cn/lnzbw/jyxx/004005/004005001/MoreInfo.aspx?CategoryNum=004005001",
                                     "http://www.lnsggzyjy.cn/lnzbw/jyxx/004005/004005001/MoreInfo.aspx?CategoryNum=004005001",
                                     "http://www.lnsggzyjy.cn/lnzbw/jyxx/004005/004005001/MoreInfo.aspx?CategoryNum=004005001")
        sectionSeeds.append(waterConservancyTender)

        trafficTender = ssd(" 交通项目",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004006/004006001/MoreInfo.aspx?CategoryNum=004006001",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004006/004006001/MoreInfo.aspx?CategoryNum=004006001",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004006/004006001/MoreInfo.aspx?CategoryNum=004006001")
        sectionSeeds.append(trafficTender)

        landTender = ssd("土地项目",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004004/004004001/MoreInfo.aspx?CategoryNum=004004001",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004004/004004001/MoreInfo.aspx?CategoryNum=004004001",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004004/004004001/MoreInfo.aspx?CategoryNum=004004001")
        sectionSeeds.append(landTender)

        medicalTender = ssd("医疗项目",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004007/004007001/MoreInfo.aspx?CategoryNum=004007001",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004007/004007001/MoreInfo.aspx?CategoryNum=004007001",
                            "http://www.lnsggzyjy.cn/lnzbw/jyxx/004007/004007001/MoreInfo.aspx?CategoryNum=004007001")
        sectionSeeds.append(medicalTender)

        gvPurchase = ssd("政府采购",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004002/004002001/MoreInfo.aspx?CategoryNum=004002001",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004002/004002001/MoreInfo.aspx?CategoryNum=004002001",
                         "http://www.lnsggzyjy.cn/lnzbw/jyxx/004002/004002001/MoreInfo.aspx?CategoryNum=004002001")
        sectionSeeds.append(gvPurchase)

        resourcesTransaction = ssd("矿权产权",
                                   "http://www.lnsggzyjy.cn/lnzbw/jyxx/004003/004003001/MoreInfo.aspx?CategoryNum=004003001",
                                   "http://www.lnsggzyjy.cn/lnzbw/jyxx/004003/004003001/MoreInfo.aspx?CategoryNum=004003001",
                                   "http://www.lnsggzyjy.cn/lnzbw/jyxx/004003/004003001/MoreInfo.aspx?CategoryNum=004003001")
        sectionSeeds.append(resourcesTransaction)

        otherTender = ssd("其他",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004008/004008001/MoreInfo.aspx?CategoryNum=004008001",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004008/004008001/MoreInfo.aspx?CategoryNum=004008001",
                          "http://www.lnsggzyjy.cn/lnzbw/jyxx/004008/004008001/MoreInfo.aspx?CategoryNum=004008001")
        sectionSeeds.append(otherTender)

        for sectionSeed in sectionSeeds:
            try:
                totalPageCount, firstPostData = self.getTotalPageCount(sectionSeed.getTotalPageUrl)
                if totalPageCount < 1:
                    return
                pageCountIndex = 1
                postRequest = {}
                postRequest["url"] = sectionSeed.getDataUrl
                postRequest["data"] = firstPostData
                while 1:
                    response = self.fetcher.post(postRequest["url"], data=postRequest["data"])
                    self.extract_detail_link(sectionSeed.initUrl, response)
                    pageCountIndex = pageCountIndex + 1
                    if pageCountIndex > totalPageCount:
                        break
                    postRequest = self.getNextPage(response.url, pageCountIndex, response.content)
            except Exception as e:
                self.logger.exception(e)

        self.logger.info("执行完成: LnsggzyjyPublicResourceTenderWorker")

    def getNextPage(self, srcUrl, pageIndex, html):
        soup = PyQuery(html, parser='html')
        postRequest = {}
        postData = {}
        formUrl = soup.find("form[name=ctl00]").attr("action")
        formUrl = urlutils.assembleUrl(srcUrl, formUrl)
        postData["__CSRFTOKEN"] = soup.find("input[id=__CSRFTOKEN]").attr("value")
        postData["__VIEWSTATE"] = soup.find("input[id=__VIEWSTATE]").attr("value")
        postData["__VIEWSTATEGENERATOR"] = soup.find("input[id=__VIEWSTATEGENERATOR]").attr("value")
        postData["__EVENTTARGET"] = "MoreInfoList1$Pager"
        postData["__EVENTARGUMENT"] = pageIndex
        postData["__EVENTVALIDATION"] = soup.find("input[id=__CSRFTOKEN]").attr("value")
        postData["MoreInfoList1$Title_txt"] = soup.find("input[id=MoreInfoList1_Title_txt]").attr("value")
        postRequest["url"] = formUrl
        postRequest["data"] = postData
        return postRequest

    def getTotalPageCount(self, getTotalPageUrl):
        """
        获取列表页分页总数
        Returns: 分页总数
        """
        # div[id=MoreInfoList1_Pager]
        response = self.fetcher.get(getTotalPageUrl)
        parser = PyQuery(response.content, parser='html')
        pageInfoElements = parser.find("div[id=MoreInfoList1_Pager]")
        pageInfo = pageInfoElements.text()
        startFlag = "总页数："
        endFlag = "当前页"
        start = pageInfo.find(startFlag)
        start = start + len(startFlag.decode('utf-8'))
        end = pageInfo.find(endFlag)
        totalPageCount = pageInfo[start:end]
        firstPostData = self.getNextPage(getTotalPageUrl, 1, response.content)["data"]
        return int(totalPageCount), firstPostData


if __name__ == "__main__":
    worker = LnsggzyjyPublicResourceTenderWorker()
    worker()
