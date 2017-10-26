#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import random
import sys

import pymongo
import requests
import time
import xlrd

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes

# from sites.court.www_jxda_gov_cn.mongo_config import TestDataDB

from conf import m_settings
from conf.m_settings import TOPICS
from libs.loghandler import getLogger
from libs.taskbase import TaskBase
from libs.tools import get_md5
from sites.common import staticproxy

from pyquery import PyQuery

basic_url = "http://www.jxda.gov.cn/ZWGK/XZQLYX/YPYLQXXZCF/index.html"
next_url = "http://www.jxda.gov.cn/ZWGK/XZQLYX/YPYLQXXZCF/list1.html"
host = "http://www.jxda.gov.cn"
MAX_RETRY = 3


# db_save = pymongo.MongoClient(TestDataDB.MONGODB_SERVER, TestDataDB.MONGODB_PORT)[TestDataDB.MONGODB_DB]
# db_save.authenticate(TestDataDB.MONGO_USER, TestDataDB.MONGO_PSW)


class www_jxda_gov_cn(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.bean_client = m_settings.beanstalk_client2()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.output_tube = m_settings.BEANSTALKD_TUBE.get('extract_info')
        self.topic_id = 68  # 需要增加"penalty": 68
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Connection": "keep-alive"
        }

    def extract_detail_link(self, response, session):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("table#Table").find("tr")
        if a is None or a == "":
            self.logger.error("列表页解析失败")
        for i in range(0, len(a) - 1):
            url = host + a.eq(i).find("a").attr("href")
            bulletin_date = a.eq(i).find("td").eq(1).text()
            self.parse_detail(url, session, bulletin_date)

    def send_data(self, extract_data):
        topic_id = self.topic_id
        url = extract_data.get('url')
        self.bean_client.put('extract_info',
                             thrift2bytes(packet(topic_id, url, extract_data)))
        # self.bean_client.put("offline_crawl_data", json.dumps(extract_data))


        # try:
        #     obj = thrift_object_generator.gen_pageparse_info(url, extract_data, topic_id)
        #     self.logger.info('put beanstalk output_tube:%s topic_id:%d' % (self.output_tube, topic_id))
        #     self.bean_client.put(self.output_tube, thrift_serialize.thriftobj2bytes(obj))
        #     return True
        # except Exception as e:
        #     self.logger.error(str(e))

    def start(self):
        self.logger.info("开始抓取江西省行政处罚数据...")
        session = requests.session()
        session.headers = self.headers
        for pageIndex in xrange(2):
            if pageIndex == 0:
                page_url = basic_url
            else:
                page_url = next_url
            try_count = 0
            while try_count < MAX_RETRY:
                try_count += 1
                try:
                    session.proxies = self.get_proxy()
                    response = session.get(page_url, timeout=30)
                    if response is not None and response.status_code == 200:
                        self.extract_detail_link(response, session)
                        break
                except requests.RequestException as e:
                    self.logger.exception(e)
                    self.logger.error("访问{}网络错误".format(basic_url))
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error("访问{}未知的错误".format(basic_url))
        self.logger.info("抓取完成, 退出程序。。")

    # 返回类型为字符串
    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为{}".format(ip))
        return ip

    def parse_detail(self, url, session, bulletin_date):
        try_count = 0
        while try_count < MAX_RETRY:
            try_count += 1
            try:
                session.proxies = self.get_proxy()
                resp = session.get(url, timeout=30)
                if resp is None:
                    continue
                pq = PyQuery(resp.text, parser="html")
                excel_url = pq.find("dt#Content").find("a").attr("href")
                if excel_url == "" or excel_url is None:
                    self.logger.error("不是excel")
                    return
                self.download_excel(excel_url, session, bulletin_date)
                break
            except requests.RequestException as e:
                self.logger.exception(e)
                self.logger.error("访问{}网络错误".format(url))
            except Exception as e:
                self.logger.exception(e)
                self.logger.error("访问{}未知的错误".format(url))
        if try_count == MAX_RETRY:
            self.logger.error("连续{}次访问详情页{}失败".format(MAX_RETRY, url))

    def download_excel(self, excel_url, session, bulletin_date):
        try_count = 0
        excel_url = host + excel_url
        while try_count < MAX_RETRY:
            try_count += 1
            try:
                session.proxies = self.get_proxy()
                resp = session.get(excel_url, timeout=30)
                if resp is None:
                    continue
                self.logger.info("下载excel内容页正常...")
                try:
                    f = open("excel.xls", "w")
                    f.write(resp.content)
                except Exception as e:
                    self.logger.error("写入excel失败")
                    self.logger.exception(e)
                finally:
                    f.close()
                self.parse_excel(bulletin_date, excel_url)
                break
            except requests.RequestException as e:
                self.logger.exception(e)
                self.logger.error("下载{}网络错误".format(excel_url))
            except Exception as e:
                self.logger.exception(e)
                self.logger.error("下载{}未知的错误".format(excel_url))
        if try_count == MAX_RETRY:
            self.logger.error("连续{}次下载{}详情页失败".format(MAX_RETRY, excel_url))

    def parse_excel(self, bulletin_date, url):
        try:
            excel = xlrd.open_workbook("excel.xls")
        except Exception as e:
            self.logger.error("打开excel失败")
            self.logger.exception(e)
            return
        sh = excel.sheet_by_index(0)
        n_cols = sh.ncols
        n_rows = sh.nrows
        check_data = sh.row_values(1)
        check_data = "".join(check_data)
        if "网址" in check_data:
            self.excel2(sh, n_rows, bulletin_date, url, n_cols)
        else:
            self.excel1(sh, n_rows, bulletin_date, url)

    def excel2(self, sh, n_rows, bulletin_date, url, n_cols):
        for i in range(2, n_rows):
            row_data = sh.row_values(i)
            penalty_id = row_data[1]
            if len(penalty_id) == 0:
                self.logger.error("excel格式有误")
                continue
            title = row_data[2]
            accused_name = row_data[3]
            accused_people = accused_name.split("，")
            case_cause = row_data[5]
            legal_basis = row_data[6]
            penalty_type = row_data[7]
            content = ""
            execute_authority = row_data[8]
            penalty_time = None
            if n_cols == 10:
                penalty_time = row_data[8]
            if n_cols == 11:
                penalty_time = row_data[9]
            if n_cols > 11:
                self.logger.error("excel格式未知")
                return
            _site_record_id = get_md5(host + case_cause.encode("utf-8") + penalty_id.encode("utf-8"))
            extract_data = {
                "province": "江西",
                "penalty_result": penalty_type,
                "penalty_type": penalty_type,
                "penalty_time": penalty_time,
                "legal_basis": legal_basis,
                "publish_time": bulletin_date,
                "case_cause": case_cause,
                "execute_authority": execute_authority,
                "title": title,
                "content": content,
                "accused_people": accused_people,
                "penalty_id": penalty_id,
                "accused_name": accused_name,
                "site": "www.jxda.gov.cn",
                "_site_record_id": _site_record_id,
                "topic_id": 68,
                "topic": "penalty",
                "url": url
            }
            # self.logger.info("_site_record_id = {}".format(_site_record_id))
            self.logger.info("案件:{0},{1}".format(case_cause.encode("utf-8"), penalty_id.encode("utf-8")))
            # self.logger.info("当前发送url = {}".format(url))
            # db_save[TestDataDB.MONGODB_COLLECTION].save(extract_data)
            self.send_data(extract_data)
            # print extract_data

    def excel1(self, sh, n_rows, bulletin_date, url):
        for i in range(4, n_rows):
            row_data = sh.row_values(i)
            penalty_id = row_data[1]
            if len(penalty_id) == 0:
                self.logger.error("excel格式有误")
                continue
            title = row_data[2]
            accused_name = row_data[3]
            accused_people = accused_name.split("，")
            case_cause = row_data[6]
            legal_basis = row_data[7].split("，")[0]
            penalty_result = ""
            try:
                penalty_result = row_data[7].split("，")[1]
            except:
                pass
            content = row_data[8]
            try:
                execute_authority = row_data[10].split("，")[0]
                penalty_time = row_data[10].split("，")[1]
            except:
                execute_authority = row_data[10].split("；")[0]
                penalty_time = row_data[10].split("；")[1]
            _site_record_id = get_md5(host + case_cause.encode("utf-8") + penalty_id.encode("utf-8"))
            extract_data = {
                "province": "江西",
                "penalty_result": penalty_result,
                "penalty_type": "",
                "penalty_time": penalty_time,
                "legal_basis": legal_basis,
                "publish_time": bulletin_date,
                "case_cause": case_cause,
                "execute_authority": execute_authority,
                "title": title,
                "content": content,
                "accused_people": accused_people,
                "penalty_id": penalty_id,
                "accused_name": accused_name,
                "site": "www.jxda.gov.cn",
                "_site_record_id": _site_record_id,
                "topic_id": 68,
                "topic": "penalty",
                "url": url

            }
            # self.logger.info("_site_record_id = {}".format(_site_record_id))
            self.logger.info("案件:{0},{1}".format(case_cause.encode("utf-8"), penalty_id.encode("utf-8")))
            # self.logger.info("当前发送url = {}".format(url))
            # db_save[TestDataDB.MONGODB_COLLECTION].save(extract_data)
            self.send_data(extract_data)
            # print extract_data


if __name__ == "__main__":
    worker = www_jxda_gov_cn()
    worker()
