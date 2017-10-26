#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  six
# @Date    2017-02-24 16:28
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup
from pyquery import PyQuery

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


class InvestmentWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")

    def extract_detail_link(self, srcUrl, response):
        html = response.text
        select = PyQuery(html, parser='html')
        detailUrlExtractItem = ExtractItem("detailUrl", True, True,
                                           "table[id=invest_info_table]>tr[class!=table_title]>td>a:contains(详情)",
                                           "href")
        resultMap= extractutils.extract(html, [detailUrlExtractItem])
        detailUrls=resultMap[detailUrlExtractItem.name]

        for detailUrl in detailUrls:
            if "" != detailUrl:
                newUrl = urlutils.assembleUrl(srcUrl, detailUrl)
                response = self.fetcher.get(newUrl)
                self.extract_detail(response)

    def getExtractItems(self):
        extractItems = []
        # 投资标题
        investTitleExtractItem = ExtractItem("investTitle", True, True,
                                                 "div[class=gw_qy_one_top]>h1", "text")
        extractItems.append(investTitleExtractItem)

        # 投资金额
        investAmountExtractItem = ExtractItem("investAmount", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(投资金额：)",
                                                  "text",neadReplaceText="投资金额：", replaceText="")
        extractItems.append(investAmountExtractItem)

        # 投资轮次
        investRoundExtractItem = ExtractItem("investRound", False, False,
                                                 "div[class=gw_qy_one]>ul>li:contains(投资轮次：)",
                                                 "text", neadReplaceText="投资轮次：", replaceText="")
        extractItems.append(investRoundExtractItem)

        # 事件简介
        investProfileExtractItem = ExtractItem("investProfile", False, False,
                                                   "div[class=gw_qy_one]:contains(描述)",
                                                   "text", startWith="描述",neadReplaceText="描述", replaceText="")
        extractItems.append(investProfileExtractItem)

        # 投资地区
        investRegionExtractItem = ExtractItem("investRegion", False, False,
                                                  "div[class=gw_qy_one]>ul>li:contains(地区：)",
                                                  "text", neadReplaceText="地区：", replaceText="")
        extractItems.append(investRegionExtractItem)

        # 投资阶段
        investStageExtractItem = ExtractItem("investStage", False, False,
                                                 "div[class=gw_qy_one]>ul>li:contains(投资阶段：)",
                                                 "text", neadReplaceText="投资阶段：", replaceText="")
        extractItems.append(investStageExtractItem)

        # 受资方公司全称
        beInvestCompanyExtractItem = ExtractItem("beInvestCompany", False, True,
                                                 "div[class=gw_qy_one]>ul>li:contains(企业名称：)",
                                                 "text", neadReplaceText="企业名称：", replaceText="")
        extractItems.append(beInvestCompanyExtractItem)

        # 投资时间
        investDateExtractItem = ExtractItem("investDate", False, True,
                                                 "div[class=gw_qy_one]>ul>li:contains(企业名称：)",
                                                 "text", neadReplaceText="企业名称：", replaceText="")
        extractItems.append(investDateExtractItem)

        # 数据来源
        investDateExtractItem = ExtractItem("investDate", False, True,
                                            "div[class=gw_qy_one]>ul>li:contains(企业名称：)",
                                            "text", neadReplaceText="企业名称：", replaceText="")
        extractItems.append(investDateExtractItem)

        return extractItems

    def extract_detail(self, response):
        extractItems = self.getExtractItems()
        #抽取投资事件基本信息
        extractResultMap = extractutils.extract(response.content, extractItems)
        #抽取投资事件投资方信息
        tableCss="table[class='table table-hover']"
        fieldColumnTrCss="tr[class=table_title]"
        dataTrCss="tr[class!=table_title]"
        tableResult= extractutils.paserTableForMany(response.content, tableCss, fieldColumnTrCss, dataTrCss)
        self.prinitConsole(extractResultMap)
        #TODO 等胡勃提供数据输出说明


    def prinitConsole(self,extractResultMap):
        primarySize=len(extractResultMap["investTitle"])
        for i in range(0,primarySize):
            printString="{"
            for key in extractResultMap:
                printString+=key+"="+extractResultMap[key][i]+","
            printString += "}"
            print  printString

    def sendData(self, data, extract_data):
        self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                 thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                     extract_data)))


    def start(self):
        pageIndexFlag = "{pageIndex}"
        urlTemplate = "http://invest.pedata.cn/list_" + pageIndexFlag + "_0_0_0_0.html"
        pageCount = self.getPageCount();
        for pageIndex in xrange(1, pageCount + 1):
            doingUrl = urlTemplate.replace(pageIndexFlag, str(pageIndex))
            response = self.fetcher.get(doingUrl)
            self.extract_detail_link(doingUrl, response)

    def getPageCount(self):
        url = "http://invest.pedata.cn/list_1_0_0_0_0.html"
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
    worker = InvestmentWorker()
    worker()
