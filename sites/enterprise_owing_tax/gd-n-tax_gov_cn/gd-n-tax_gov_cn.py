#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time: 2017/8/28 下午3:15
@Author: CZC
@File: gd-n-tax_gov_cn.py
"""
import sys
from urlparse import urljoin

import xlrd
from lxml import etree

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import util
from sites.common.requests_with_proxy import requester
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger


BASE_URL = "http://www.gd-n-tax.gov.cn/pub/001032/xxgk/tzgg/ssgg/index.html"
MAX_RETRY = 5
TIMEOUT = 60


class GdNTaxGovCnSpider(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client2()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")

        self.turn_page_url = "http://www.gd-n-tax.gov.cn/pub/001032/xxgk/tzgg/ssgg/index_{}.html"

    def start(self):
        pages = self.get_pages()
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for page in xrange(0, pages + 1):
            url = self.turn_page_url.format(page)
            if page == 0:
                url = BASE_URL
            response = requester(url, max_retry=MAX_RETRY, timeout=TIMEOUT)
            if response is None:
                continue
            detail_urls = self.get_detail_urls(response)
            for ear_url in detail_urls:
                detail_response = requester(ear_url, max_retry=MAX_RETRY, timeout=TIMEOUT)
                if detail_response is None:
                    continue

                self.parse(detail_response)

    @staticmethod
    def get_detail_urls(response):
        detail_urls = []
        tree = etree.HTML(response.content)
        list_href = tree.xpath("//div[@class='tab_con_main box']/ul/li/a/@href")
        for href in list_href:
            url = urljoin(response.url, href)
            # url = urlutils.assembleUrl(response.url, href)
            detail_urls.append(url)
        return detail_urls

    def get_pages(self):
        response = requester(BASE_URL, max_retry=MAX_RETRY, timeout=TIMEOUT)
        if response is None:
            self.logger.warning('获取页数失败，正在重试……')
            return self.get_pages()
        pages = util.get_match_value('createPageHTML\(', ',', response.content, True)
        return int(pages[1])

    # def get_proxy(self):
    #     all_ip = self.all_ip
    #     ip = all_ip[random.randint(0, len(all_ip) - 1)]
    #     self.logger.info("更换ip为:{}".format(ip))
    #     return ip
    #
    # def requester(self, url):
    #     session = requests.session()
    #     session.proxies = self.get_proxy()
    #     try_count = 0
    #     while try_count < MAX_RETRY:
    #         try_count += 1
    #         try:
    #             response = session.get(url, timeout=TIMEOUT)
    #             if response.status_code == 200 and response is not None:
    #                 return response
    #
    #         except Exception as e:
    #             self.logger.error("访问{}出现未知的错误".format(url))
    #             self.logger.exception(e)
    #         self.logger.error("{}次重试访问{}页面失败".format(MAX_RETRY, url))
    #     return

    def parse(self, response):
        self.logger.info('数据抓取成功，正在解析 {}数据……'.format(response.url))

        tree = etree.HTML(response.content)
        href = tree.xpath("//div[@class='relnews'][1]/a/@href")
        if not href:
            href = tree.xpath("//div[@id='contentpp']/p[3]/a/@href")
            if not href:
                self.logger.error('{}站点没有文件可供下载，请检查'.format(response.url))
                return
        data_url = urljoin(response.url, href[0])
        data_response = requester(data_url)
        if data_response is None:
            self.logger.error('{}站点下载文件失败,请检查'.format(data_url))
            return

        bulletin_date = tree.xpath("substring-after(//div[@class='contentdata']/span[1], '%s')" % u'日期：')  # 公告日期

        if 'xls' in data_url[-4:]:
            try:
                data = xlrd.open_workbook(file_contents=data_response.content)
            except:
                self.logger.error('{}excel受保护无法打开，已跳过'.format(data_url))
                return

            table = data.sheets()[0]
            rows = table.nrows
            try:
                # 循环行列表数据
                for i in xrange(1, rows):  # 除去表头
                    per_row = table.row_values(i)
                    parse_data = {
                        'taxpayer_name': per_row[0],
                        'taxpayer_id': per_row[1],
                        'legalman': per_row[2],
                        'legal_man_id': per_row[3],
                        'business_address': per_row[4],
                        'tax_item': per_row[5],
                        'owing_tax': per_row[6] * 10000,  # '{0}{1}'.format(per_row[6], '万元'),

                        'bulletin_date': bulletin_date,
                        'province': u'广东',
                        '_site_record_id': '{0}{1}{2}'.format(per_row[1], per_row[5], per_row[6]),
                        'url': data_url,

                    }
                    self.send_data(parse_data)
            except:
                self.logger.error('{0}站点的Excel非正确数据，跳过'.format(data_url))

            self.logger.info('本页数据解析完成，已发往消息队列……')
        elif 'doc' in data_url[-4:]:
            pass

    def send_data(self, extract_data):
        topic_id = m_settings.TOPICS.get('enterprise_owing_tax')
        url = extract_data.get('url')

        self.beans_client.put('extract_info',
                              thrift2bytes(packet(topic_id, url, extract_data)))


if __name__ == "__main__":
    worker = GdNTaxGovCnSpider()
    worker()
