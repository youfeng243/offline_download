#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Time: 2017/8/28 下午3:15
@Author: CZC
@File: yz_jsds_gov_cn.py
"""
import sys
from StringIO import StringIO
from urlparse import urljoin

import xlrd
import docx

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
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

BASE_URL = "http://yz.jsds.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?perpage=200&col=1&appid=1&webid=13&path=%2F&columnid=58225&unitid=84438&webname=%E6%B1%9F%E8%8B%8F%E7%9C%81%E6%89%AC%E5%B7%9E%E5%9C%B0%E6%96%B9%E7%A8%8E%E5%8A%A1%E5%B1%80&permissiontype=0"
MAX_RETRY = 5
TIMEOUT = 60


class YzJsdsGovCnSpider(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")

    def start(self):
        while True:
            response = requester(BASE_URL, max_retry=MAX_RETRY, timeout=TIMEOUT)
            if response is not None:
                break
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
        list_href = tree.xpath("//a/@href")
        for href in list_href:
            current_href = util.get_match_value("\\\'", "\\\\", href)
            url = urljoin(response.url, current_href)
            detail_urls.append(url)
        return detail_urls

    def parse(self, response):
        self.logger.info('数据抓取成功，正在解析 {}数据……'.format(response.url))

        tree = etree.HTML(response.content)
        bulletin_date = tree.xpath("substring-after(//div[@id='pubdate'], '%s')" % u'发布时间：')
        href = tree.xpath("//div[@id='contentText']//a/@href")  # doc, xls
        if href:
            data_url = urljoin(response.url, href[0])
            # 测试用url
            # data_url = 'http://yz.jsds.gov.cn/module/download/downfile.jsp?classid=0&filename=160119113716798.docx'
            # data_url = 'http://yz.jsds.gov.cn/module/download/downfile.jsp?classid=0&filename=170510154351373.docx'
            # data_url = 'http://yz.jsds.gov.cn/module/download/downfile.jsp?classid=0&filename=150902125138208.docx'

            data_response = requester(data_url)
            if data_response is None:
                self.logger.error('{}站点下载文件失败,请检查'.format(data_url))
                return
            current_data_url = util.get_match_value("location='", "';", data_response.content)
            current_data_response = requester(current_data_url)
            if current_data_response is None:
                self.logger.error('{}站点下载文件失败,请检查'.format(data_url))
                return

            if 'xls' in data_url[-4:]:
                try:
                    data = xlrd.open_workbook(file_contents=current_data_response.content)
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error('{} excel受保护无法打开，已跳过'.format(current_data_url))
                    return

                table = data.sheets()[0]
                rows = table.nrows
                # 获取schema索引
                schema_list = table.row_values(1)
                schema = {}
                for index, title in enumerate(schema_list):
                    if title == u'纳税人识别号':
                        schema['taxpayer_id'] = index
                    elif title == u'纳税人名称':
                        schema['taxpayer_name'] = index
                    elif title == u'法定代表人（负责人）姓名':
                        schema['legalman'] = index
                    elif title == u'身份证件号码':
                        schema['legal_man_id'] = index
                    elif title == u'生产经营地址':
                        schema['business_address'] = index
                    elif title == u'欠税税种':
                        schema['tax_item'] = index
                    elif title == u'税费所属期起':
                        schema['owing_date'] = index
                    elif title == u'欠税余额':
                        schema['owing_tax'] = index
                    elif title == u'当期新发生欠税':
                        schema['owing_tax_cur_period'] = index
                    elif title == u'主管税务所（科、分局）':
                        schema['tax_authority'] = index

                # 循环行列表数据
                for i in xrange(2, rows):  # 除去表头
                    try:
                        parse_data = {}
                        per_row = table.row_values(i)
                        for title, index in schema.iteritems():
                            if title == 'owing_tax' and not type(per_row[index]) == float:
                                per_row[index] = float(per_row[index].replace(',', ''))
                            elif title == 'tax_item':
                                per_row[index] = per_row[index].split('|')[-1]
                            elif title == 'owing_tax_cur_period' and not type(per_row[index]) == float:
                                per_row[index] = float(per_row[index].replace(',', ''))
                            parse_data[title] = per_row[index]

                        parse_data['_site_record_id'] = '{0}{1}{2}'.format(parse_data.get('taxpayer_id'),
                                                                           parse_data.get('tax_item'),
                                                                           parse_data.get('owing_tax'))
                        parse_data['url'] = data_url
                        parse_data['province'] = u'江苏'
                        parse_data['bulletin_date'] = bulletin_date

                        self.send_data(parse_data)
                    except Exception as e:
                        self.logger.error('{0}站点的Excel非正确数据，跳过'.format(data_url))
                        self.logger.exception(e)

                self.logger.info('本页数据解析完成，已发往消息队列……')

            elif 'doc' in data_url[-4:]:
                # self.logger.info('doc {}'.format(current_data_url))
                try:
                    data = docx.Document(StringIO(current_data_response.content))
                    xml = data.element.xml

                    root = ET.fromstring(xml)
                    # for child in root.iter():
                    #     print child.tag, '\t\t\t', child.attrib, '\n', child.text
                    element_list = root.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr")
                    #  [@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rsidRPr='004E3F0D']
                    # # 补丁
                    # if not element_list:
                    #     element_list = root.findall(
                    #         ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr[@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rsidR='004B7C82']")
                    # if not element_list:
                    #     element_list = root.findall(
                    #         ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr[@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rsidRPr='00AF1E97']")

                    # 获取schema索引
                    schema_list = element_list[4].findall(
                        ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                    schema = {}
                    for index, title in enumerate(schema_list):
                        title = title.text
                        if title == u'纳税人识别号':
                            schema['taxpayer_id'] = index
                        elif title == u'纳税人名称':
                            schema['taxpayer_name'] = index
                        elif title == u'法定代表人（负责人）姓名':
                            schema['legalman'] = index
                        elif title == u'身份证件号码':
                            schema['legal_man_id'] = index
                        elif title == u'生产经营地址':
                            schema['business_address'] = index
                        elif title == u'欠税税种':
                            schema['tax_item'] = index
                        elif title == u'税费所属期起':
                            schema['owing_date'] = index
                        elif title == u'欠税余额':
                            schema['owing_tax'] = index
                        elif title == u'当期新发生欠税':
                            schema['owing_tax_cur_period'] = index
                        elif title == u'主管税务所（科、分局）':
                            schema['tax_authority'] = index
                    # 循环行列表数据
                    for element in element_list[5:]:
                        parse_data = {}
                        per_row = element.findall(
                            ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t")
                        if not per_row:
                            continue
                        for title, index in schema.iteritems():
                            try:
                                per_row[index] = per_row[index].text
                                if title == 'owing_tax' and not type(per_row[index]) == float:
                                    per_row[index] = float(per_row[index].replace(',', ''))
                                elif title == 'tax_item':
                                    per_row[index] = per_row[index].split('|')[-1]
                                elif title == 'owing_tax_cur_period' and not type(per_row[index]) == float:
                                    per_row[index] = float(per_row[index].replace(',', ''))
                                parse_data[title] = per_row[index]
                            except (UnicodeEncodeError, IndexError, ValueError):
                                self.logger.error('doc中一条数据不规范，此条跳过'.format(current_data_url))
                            except Exception as e:
                                self.logger.error('{0} doc解析发生未知错误，请检查'.format(current_data_url))
                                self.logger.exception(e)

                            parse_data['_site_record_id'] = '{0}{1}{2}'.format(parse_data.get('taxpayer_id'),
                                                                               parse_data.get('tax_item'),
                                                                               parse_data.get('owing_tax'))
                            parse_data['url'] = current_data_url
                            parse_data['province'] = u'江苏'
                            parse_data['bulletin_date'] = bulletin_date
                            if len(parse_data) >= 6:
                                self.send_data(parse_data)

                    self.logger.info('本页数据解析完成，已发往消息队列……')

                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error('{} doc无法打开，已跳过'.format(current_data_url))
                    return

        else:
            # self.logger.info('text {}'.format(response.url))
            data = tree.xpath("//*[@id='contentText']//tr")
            for per_data in data[1:]:
                per_row = per_data.xpath("./td//text()")
                per_row = [value for value in per_row if '\n' not in value]
                try:
                    parse_data = {
                        'taxpayer_name': per_row[1],
                        'taxpayer_id': per_row[2],
                        'business_address': per_row[3],
                        'tax_item': per_row[4].split('|')[-1],
                        'owing_tax': per_row[5],
                        '_site_record_id': '{0}{1}{2}'.format(per_row[1],
                                                              per_row[4],
                                                              per_row[5]),
                        'url': response.url,
                        'province': u'江苏',
                        'bulletin_date': bulletin_date,
                    }
                    if len(per_row) == 7:
                        parse_data['owing_tax_cur_period'] = per_row[6]

                except Exception as e:
                    self.logger.error('{} 发生未知错误，请检查'.format(response.url))
                    self.logger.exception(e)
            self.logger.info('本页数据解析完成，已发往消息队列……')

    def send_data(self, extract_data):
        topic_id = m_settings.TOPICS.get('enterprise_owing_tax')
        url = extract_data.get('url')

        self.beans_client.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                              thrift2bytes(packet(topic_id, url, extract_data)))


if __name__ == "__main__":
    worker = YzJsdsGovCnSpider()
    worker()
