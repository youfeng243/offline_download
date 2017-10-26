#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  six
# @Date    2017-02-24 16:28
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup

sys.path.append("..")
sys.path.append("../..")

from conf import m_settings
from libs.fetcher import Fetcher
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
import re
from sites.common import urlutils, stringutils, extractutils
from sites.common.pyqueryutils import ExtractItem

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


class FinancingWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")

    def extract_detail_link(self, srcUrl, response):
        html = response.text
        extractItems=[]
        # 抽取融资事件的公司详情url
        financingCompanyDetailUrlExtractItem = ExtractItem("financingCompanyDetail", True, True,
                                           "table[id=need_info_table]>tr[class!=table_title]>td:eq(0)>a",
                                           "href")
        extractItems.append(financingCompanyDetailUrlExtractItem)

        #抽取融资事件详情url
        financingDetailUrlExtractItem = ExtractItem("financingDetailUrl", False, True,
                                           "table[id=need_info_table]>tr[class!=table_title]>td>a:contains(详情)",
                                           "href")
        extractItems.append(financingDetailUrlExtractItem)

        # 融资事件地区
        regionExtractItem = ExtractItem("region", False, True,
                                                    "table[id=need_info_table]>tr[class!=table_title]>td:eq(1)",
                                                    "text")
        extractItems.append(regionExtractItem)

        # 融资公司行业
        industryExtractItem = ExtractItem("industry", False, True,
                                        "table[id=need_info_table]>tr[class!=table_title]>td:eq(2)",
                                        "text")
        extractItems.append(industryExtractItem)

        resultMap= extractutils.extract(html, extractItems)

        financingCompanyDetailUrls = resultMap[financingCompanyDetailUrlExtractItem.name]
        financingDetailUrls=resultMap[financingDetailUrlExtractItem.name]
        regions=resultMap[regionExtractItem.name]
        industrys = resultMap[industryExtractItem.name]

        loopSize=len(financingDetailUrls)
        for i in range(0,loopSize):
            financingCompanyDetailUrl=financingCompanyDetailUrls[i]
            financingDetailUrl = financingDetailUrls[i]
            region=regions[i]
            industry = industrys[i]
            if "" != financingCompanyDetailUrl and "" != financingDetailUrl:
                #组装融资公司详情页和融资事件详情页url
                financingCompanyDetailUrl = urlutils.assembleUrl(srcUrl, financingCompanyDetailUrl)
                financingDetailUrl = urlutils.assembleUrl(srcUrl, financingDetailUrl)
                #先处理融资公司详情页
                response = self.fetcher.get(financingCompanyDetailUrl)
                financingCompanyDetai=self.extractFinancingCompanyDetai(response)
                financingCompanyDetai["region"]=[region]
                financingCompanyDetai["industry"] = [industry]
                #在处理融资事件详情页
                response = self.fetcher.get(financingDetailUrl)
                self.extractFinancingDetail(response,financingCompanyDetai)

    def extractFinancingCompanyDetai(self,response):
        extractItems=self.getFinancingCompanyExtractItems()
        extractResultMap = extractutils.extract(response.content, extractItems)
        return extractResultMap

    def extractFinancingDetail(self, response,financingCompanyDetai):
        extractItems = self.getFinancingExtractItems()
        extractResultMap = extractutils.extract(response.content, extractItems)
        self.prinitConsole(extractResultMap)

    def getFinancingExtractItems(self):
        extractItems = []
        # 投资标题
        investTitleExtractItem = ExtractItem("investTitle", True, True,
                                                 "div[class=gw_qy_one_top]>h1", "text")
        extractItems.append(investTitleExtractItem)

        # 融资项目名称
        financingProjectExtractItem = ExtractItem("financingProject", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(项目名称：)",
                                                  "text",neadReplaceText="项目名称：", replaceText="")
        extractItems.append(financingProjectExtractItem)

        # 发布时间
        publishDateExtractItem = ExtractItem("publishDate", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(发布时间：)",
                                                  "text", neadReplaceText="发布时间：", replaceText="")
        extractItems.append(publishDateExtractItem)

        # 融资轮次
        financingRoundExtractItem = ExtractItem("financingRound", False, False,
                                                 "div[class=gw_qy_one]>ul>li:contains(轮次：)",
                                                 "text", neadReplaceText="轮次：", replaceText="")
        extractItems.append(financingRoundExtractItem)

        # 出让股权
        proportionShareTransferExtractItem = ExtractItem("proportionShareTransfer", False, False,
                                                   "div[class=gw_qy_one]>ul>li:contains(出让股权：)",
                                                   "text",neadReplaceText="出让股权：", replaceText="")
        extractItems.append(proportionShareTransferExtractItem)

        # 融资方式
        financingModeExtractItem = ExtractItem("financingMode", False, False,
                                                 "div[class=gw_qy_one]>ul>li:contains(融资方式：)",
                                                 "text", neadReplaceText="融资方式：", replaceText="")
        extractItems.append(financingModeExtractItem)

        # 信息来源
        informationSourcesExtractItem = ExtractItem("informationSources", False, True,
                                                 "div[class=gw_qy_one]>ul>li:contains(信息来源：)",
                                                 "text", neadReplaceText="信息来源：", replaceText="")
        extractItems.append(informationSourcesExtractItem)

        # 描述
        describeExtractItem = ExtractItem("investProfile", False, False,
                                                   "div[class=gw_qy_one]:contains(描述)",
                                                   "text", substringStart="描述",substringEnd="项目亮点")
        extractItems.append(describeExtractItem)

        # 项目亮点
        projectHighlightsExtractItem = ExtractItem("projectHighlights", False, False,
                                                   "div[class=gw_qy_one]:contains(描述)",
                                                   "text", substringStart="项目亮点",substringEnd="盈利模式")
        extractItems.append(projectHighlightsExtractItem)

        return extractItems

    def prinitConsole(self,extractResultMap):
        primarySize=len(extractResultMap["investTitle"])
        for i in range(0,primarySize):
            printString="{"
            for key in extractResultMap:
                printString+=key+"="+extractResultMap[key][i]+","
            printString += "}"
            print  printString

    def getFinancingCompanyExtractItems(self):
        extractItems = []
        # 融资公司全称
        enterpriseFullNameExtractItem = ExtractItem("enterpriseFullName", True, True,
                                                 "div[class=gw_qy_one_top]>h1", "text")
        extractItems.append(enterpriseFullNameExtractItem)

        # 融资企业中文简称
        enterpriseShortNameExtractItem = ExtractItem("enterpriseShortName", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(中文简称：)",
                                                  "text",neadReplaceText="中文简称：", replaceText="")
        extractItems.append(enterpriseShortNameExtractItem)

        # 融资企业英文简称
        enterpriseShortNameEnExtractItem = ExtractItem("enterpriseShortNameEn", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(英文简称：)",
                                                  "text", neadReplaceText="英文简称：", replaceText="")
        extractItems.append(enterpriseShortNameEnExtractItem)
        return extractItems

    def sendData(self, data, extract_data):
        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                     extract_data)))


    def start(self):
        pageIndexFlag = "{pageIndex}"
        urlTemplate = "http://need.pedata.cn/list_" + pageIndexFlag + "_0_0_0_0.html"
        pageCount = self.getPageCount();
        for pageIndex in xrange(1, pageCount + 1):
            doingUrl = urlTemplate.replace(pageIndexFlag, str(pageIndex))
            response = self.fetcher.get(doingUrl)
            self.extract_detail_link(doingUrl, response)

    def getPageCount(self):
        url = "http://need.pedata.cn/list_1_0_0_0_0.html"
        response = self.fetcher.get(url)
        bsoup = BeautifulSoup(response.text)
        scripts = bsoup.select("script")
        pageCount = 0
        for script in scripts:
            scriptHtml = script.get_text()
            pageCountStr = stringutils.substringBetween(scriptHtml, "var totalPage =", ";")
            if pageCountStr is not None:
                pageCount = int(pageCountStr)
                break
        return pageCount


if __name__ == "__main__":
    worker = FinancingWorker()
    worker()
