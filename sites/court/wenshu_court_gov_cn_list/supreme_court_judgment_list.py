#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'

import sys
import time
import random
import json

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
from sites.common import urlutils, extractutils, queue
from sites.common.pyqueryutils import ExtractItem
from sites.common.page import Page
from sites.common.chrome_selenium import ChromeSelenium

post_data = {

}

headMap = {}
headMap["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
headMap["Accept-Language"] = "zh-CN,zh;q=0.8"
headMap["Cache-Control"] = "max-age=0"
headMap[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
headMap["Upgrade-Insecure-Requests"] = "1"


class SupremeCourtJudgmentListWorker(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.siteHost = "wenshu.court.gov.cn"
        chromedriverPath = "/home/work/webdriver/chromedriver"
        proxyConnection = "HDW0OWP3S3E4M8TD:3CC9C9FEB5EF1175@proxy.abuyun.com:9020"
        #proxyConnection = "bjhz:bjhz@182.107.87.225:7777"
        self.downer = ChromeSelenium(chromedriverPath, intervalTime=3000, proxyConnection=proxyConnection)
        #self.downer = ChromeSelenium(chromedriverPath, intervalTime=3000, proxyHost="119.29.113.154", proxyPort=8080)
        #self.downer = ChromeSelenium(chromedriverPath, intervalTime=3000,)
        self.queue = queue.Queue("supreme_court_list")
        self.detailQueue = queue.Queue("supreme_court_detail")

    def setSearchItem(self, xpath, value):
        element = self.downer.getDriver().find_element_by_xpath(xpath)
        value = value.decode('utf-8')
        element.send_keys(value)

    def doSearchItem(self, searchItemMap):
        if searchItemMap is not None and len(searchItemMap) > 0:
            searchItemDivXpath = "//div[@id='head_maxsearch_btn']"
            element = self.downer.getDriver().find_element_by_xpath(searchItemDivXpath)
            element.click()

        isClickSearchBt = False

        completxt = searchItemMap.get("completxt", None)
        if completxt is not None:
            completxtXpath = "//input[@id='completxt']"
            self.setSearchItem(completxtXpath, completxt)
            isClickSearchBt = True

        caseName = searchItemMap.get("caseName", None)
        if caseName is not None:
            caseNameXpath = "//input[@id='adsearch_AJMC']"
            self.setSearchItem(caseNameXpath, caseName)
            isClickSearchBt = True

        caseType = searchItemMap.get("caseType", None)
        if caseType is not None:
            caseTypeXpath = "//input[@id='9_input']"
            self.setSearchItem(caseTypeXpath, caseType)
            isClickSearchBt = True

        courtLevel = searchItemMap.get("courtLevel", None)
        if courtLevel is not None:
            courtLevelXpath = "//input[@id='8_input']"
            self.setSearchItem(courtLevelXpath, courtLevel)
            isClickSearchBt = True

        courtName = searchItemMap.get("courtName", None)
        if courtName is not None:
            courtNameXpath = "//input[@id='adsearch_SLFY']"
            self.setSearchItem(courtNameXpath, courtName)
            isClickSearchBt = True

        startDate = searchItemMap.get("startDate", None)
        if startDate is not None:
            startDateXpath = "//input[@id='beginTimeCPRQ']"
            self.setSearchItem(startDateXpath, startDate)
            isClickSearchBt = True

        endDate = searchItemMap.get("endDate", None)
        if endDate is not None:
            endDateXpath = "//input[@id='endTimeCPRQ']"
            self.setSearchItem(endDateXpath, endDate)
            isClickSearchBt = True

        if isClickSearchBt:
            clickSearchBtXpath = "//input[@id='list_btnmaxsearch']"
            element = self.downer.getDriver().find_element_by_xpath(clickSearchBtXpath)
            element.click()

    def getSearchStr(self,searchItemMap):
        printString = ""
        for key in searchItemMap:
            printString += key + "=" + searchItemMap[key]+ ","
        printString=printString[0:len(printString)-1]
        return printString

    def start(self):
        seed = "http://wenshu.court.gov.cn/List/List"
        docidFlag = "{docid}"
        judgmentDetailUrlCount = 0
        judgmentDetailUrlTemplate = "http://wenshu.court.gov.cn/content/content?DocID=" + docidFlag
        extractItems = []
        detailUrlExtractItem = ExtractItem("detailUrl", True, True,
                                           "div[class=wstitle]>a",
                                           "href")
        extractItems.append(detailUrlExtractItem)
        searchItemMap = {}
        searchItemMap["案件类型"]="刑事案件"
        startTime = time.time()
        # 通过浏览器执行 仿造ajax post请求后台数据
        # 全文检索:全文检索,案由:民事案由,
        # 案件名称:案件名称,案号:案号,
        # 法院名称:法院名称,法院层级:最高法院,
        # 案件类型:民事案件,审判程序:一审,
        # 文书类型:调解书,裁判日期:2017-07-10 TO 2017-07-18,
        # 审判人员:审判人员, 当事人:当事人,
        # 律所:律所,律师:律师,法律依据:法律依据
        resultDivId = "six_liu"
        paramFlag = "{param}"
        pageIndexFlag = "{pageIndex}"
        pageCountFlag = "{pageCount}"
        orderFlag = "{order}"
        directionFlag = "{direction}"

        ajaxPostTemplate = "$.ajax({" \
                           "url:\"/List/ListContent\"," \
                           "type: \"POST\"," \
                           "async: true," \
                           "data: {" \
                                    "\"Param\": \"案件类型:"+paramFlag+"\"," \
                                    " \"Index\": "+pageIndexFlag+"," \
                                    " \"Page\": "+pageCountFlag+", " \
                                    "\"Order\": \""+orderFlag+"\"," \
                                    " \"Direction\": \""+directionFlag+"\"" \
                                    "},success: function(data) {" \
                                        "var html =$(\"html\");" \
                                        "var result =$(\"<div id='"+resultDivId+"'>\" + data + \"</div>\");" \
                                        "html.append(result);" \
                                        "console.info(data);" \
                                        "}" \
                                    "});"
        param=self.getSearchStr(searchItemMap)
        pageIndex = 1
        pageCount = 20
        order = "法院层级"
        direction = "asc"
        totalPageCount=0
        isExtractFirstPage=False
        try:
            self.downer.down(seed)
            while True:
                srcUrl = self.downer.getDriver().current_url
                try:
                    element = self.downer.getDriver().find_element_by_xpath("//div[@class='wstitle']/a")
                    if element is None:
                        self.downer.getDriver().refresh()
                        continue
                    else:
                        if isExtractFirstPage==False:
                            html=self.downer.getHtml()
                            extractResultMap=extractutils.extract(html,extractItems)
                            detailUrls=extractResultMap[detailUrlExtractItem.name]
                            isExtractFirstPage=True
                            for i in range(0,len(detailUrls)):
                                judgmentDetailUrl=detailUrls[i]
                                judgmentDetailUrl=urlutils.assembleUrl(srcUrl,judgmentDetailUrl)
                                page = Page(url=judgmentDetailUrl, referer=srcUrl)
                                self.detailQueue.push(page)
                                judgmentDetailUrlCount = judgmentDetailUrlCount + 1

                except Exception as e:
                    self.logger.exception(e)
                    self.downer.getDriver().refresh()
                    time.sleep(5)
                    continue
                # self.doSearchItem(searchItemMap)

                ajaxPost = ajaxPostTemplate.replace(paramFlag, param)
                ajaxPost = ajaxPost.replace(pageIndexFlag, str(pageIndex))
                ajaxPost = ajaxPost.replace(pageCountFlag, str(pageCount))
                ajaxPost = ajaxPost.replace(orderFlag, order)
                ajaxPost = ajaxPost.replace(directionFlag, direction)

                self.downer.getDriver().execute_script(ajaxPost)
                time.sleep(20)
                dataJson=""
                try:
                    element = self.downer.getDriver().find_element_by_id(resultDivId)
                    dataJson = element.text
                    delDiv = "$('#six_liu').remove();"
                    self.downer.getDriver().execute_script(delDiv)
                except Exception as e:
                    self.logger.exception(e)
                if dataJson=="":
                    continue
                else:
                    delDiv="$('#six_liu').remove();"
                    self.downer.getDriver().execute_script(delDiv)
                totalCount,docids = self.getDocids(dataJson)
                for docid in docids:
                    judgmentDetailUrl = judgmentDetailUrlTemplate.replace(docidFlag, docid)
                    page = Page(url=judgmentDetailUrl, referer=srcUrl)
                    self.detailQueue.push(page)
                    judgmentDetailUrlCount = judgmentDetailUrlCount + 1

                endTime = time.time()
                print "collection data:" + str(judgmentDetailUrlCount) + " and ealapsed time:" + str(
                    endTime - startTime)
                time.sleep(random.randint(10, 20))

                if totalPageCount==0:
                    if totalCount%pageCount==0:
                        totalPageCount=totalCount/pageCount
                    else:
                        totalPageCount = totalCount / pageCount+1
                pageIndex=pageIndex+1
                if pageIndex>totalPageCount:
                    break
        except Exception as e:
            self.logger.exception(e)
        finally:
            if self.downer is not None:
                self.downer.close()

    def getDocids(self, dataJson):
        docids = []
        dataArray = eval("(" + dataJson + ")")
        size = len(dataArray)
        for i in range(1, size):
            docid = dataArray[i]["文书ID"]
            docids.append(docid)
        return int(dataArray[0]["Count"]),docids


if __name__ == "__main__":
    worker = SupremeCourtJudgmentListWorker()
    worker()

