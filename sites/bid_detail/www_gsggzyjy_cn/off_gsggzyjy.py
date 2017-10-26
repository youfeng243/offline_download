#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-24 16:28
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.bid_detail.common import parser_content

from conf import m_settings
from libs.fetcher import Fetcher
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from libs.taskbase import TaskBase
from libs.loghandler import getLogger
import re
from pyquery import PyQuery as py

detail_link_regx = re.compile("""href='\s*(cpwsplay.*?)'""")
detail_title_regx = re.compile("""href='\s*cpwsplay.*?>(.*?)</a>""")
pdf_link_regx = re.compile('<iframe.*?src="(.*?)"')
title_regx = re.compile('<div.*?title.*>(.*?)</div>')


class GsggzyjyCrawler(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beanstalkclient = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")

    def extract_detail_link(self, response):
        url_list = py(response.content, parser='html')
        for i in range(0, len(url_list.find('li.liClass'))):
            url = url_list.find('li.liClass').eq(i).find('a').attr('href')
            self.fetcher.async_get(url="http://www.gsggzyjy.cn" + url, callback=self.extract_pdf_link)

    def extract_pdf_link(self, response):
        pdf_link = str(response.content).split('下载公告PDF文件')[0].split('href="')[-1].split('"')[0]
        filename = pdf_link.split('.pdf')[0].split('/')[-1] + ".pdf"
        parser = py(response.content, parser='html')
        title = ''
        publish_time = ''
        try:
            title = parser.find('div.infotitle').eq(0).text().split(' ')[0]
            publish_time = str(response.content).split('开标时间：')[1].split('<')[0]
        except Exception as e:
            self.logger.exception(e)

        data = self.fetcher.download_file(pdf_link, filename=filename)
        data['title'] = title
        data['publish_time'] = publish_time
        extract_data = parser_content.deal(data)
        if extract_data:
            self.beanstalkclient.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                                     thrift2bytes(packet(m_settings.TOPICS['bid_detail'], data['sourceUrl'],
                                                         extract_data)))

    def start(self):
        self.logger.info("开始执行: GsggzyjyCrawler")
        siteitem = ['71', '73', '77', '80', '91', '92', '86', '89']
        for url in siteitem:
            try:
                resp = self.fetcher.get(
                    "http://www.gsggzyjy.cn/InfoPage/AnnoGoodsList.aspx?SiteItem={0}&page=1&query=".format(url))
                total_page = int(
                    str(resp.content).split('ContentPlaceHolder1_AnnoGoodsList_lblPageCount"><b>')[1].split('<')[0])
                if total_page < 1:
                    return
                for i in xrange(1, total_page):
                    self.fetcher.async_get(
                        "http://www.gsggzyjy.cn/InfoPage/AnnoGoodsList.aspx?SiteItem={0}&page={1}&query=".format(url,
                                                                                                                 i),
                        callback=self.extract_detail_link)
                self.fetcher.join_all()
            except Exception as e:
                self.logger.exception(e)
        self.logger.info("执行完成: GsggzyjyCrawler")


if __name__ == "__main__":
    c = GsggzyjyCrawler()
    c()
