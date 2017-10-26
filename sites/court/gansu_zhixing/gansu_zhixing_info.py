#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import random
import re
import sys
import requests
from pyquery import PyQuery

reload(sys)
sys.setdefaultencoding("utf8")

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger

pdf_url = "http://61.178.55.5:7080/susong51/pub/zxgk/detail.htm?bh={}&fy=3750"
basic_url = "http://61.178.55.5:7080/susong51/fymh/3750/zxgk.htm?bzxrmc=&sxlx=&zjhm=&bzxrlx=&jbfy=&page={}"
max_retry = 3
timeout = 40


def get_last_url():
    try:
        f = open("gansu_court_zhixing.txt")
        return f.read()
    except:
        return ""


class Gansu_zhixing(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.bean_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",

        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.last_url = get_last_url()

    def extract_detail_link(self, response, session, pageindex):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("table.fd_table_03 ").find("tr")
        for i in range(1, len(a)):
            title = a.eq(i).find("td").eq(1).text()
            bh_id = a.eq(i).find("td").eq(1).attr("onclick")
            bh_id = re.findall(r"'(.+)'", bh_id)[0]
            if "" != id:
                self.extract_pdf_link(bh_id, title, session, i, pageindex)

    def extract_pdf_link(self, bh_id, title, session, i, pageindex):
        detail_link = pdf_url.format(bh_id)
        if pageindex == 1 and i == 1:
            with open("gansu_court_zhixing.txt", "w") as f:
                f.write(detail_link)
        if detail_link == self.last_url:
            sys.exit()
        try_count = 0
        while try_count < max_retry:
            try:
                try_count += 1
                response = session.get(detail_link, timeout=timeout)
                if response is not None and response.status_code == 200:
                    pq = PyQuery(response.text, parser="html")
                    trs = pq.find("table.fd_table_02").find("div")
                    data = {}

                    for i in xrange(0, len(trs), 2):
                        text_key = trs.eq(i).text()
                        text_value = trs.eq(i + 1).text()
                        data[text_key] = text_value
                    extract_data = {}
                    extract_data["case_state"] = data.get(u"案件状态", "")
                    extract_data["court"] = data.get(u"执行法院", "")
                    extract_data["case_date"] = data.get(u"立案日期", "")
                    extract_data["i_name"] = data.get(u"被执行人姓名/名称", "")
                    extract_data["party_card_num"] = data.get(u"证件号码", "")
                    extract_data["exec_money"] = data.get(u"申请执行标的金额", "")
                    extract_data["max_money"] = data.get(u"申请执行标的金额", "")
                    extract_data["sum_money"] = data.get(u"申请执行标的金额", "")
                    extract_data["money_unit"] = "元"
                    extract_data["province"] = "甘肃"
                    extract_data["case_id"] = data.get(u"执行依据文书编号", "")
                    extract_data["url"] = detail_link
                    extract_data["source"] = "gansu_zhixing_info"
                    extract_data["topic"] = "zhixing_info"
                    extract_data["_site_record_id"] = "gansu_court"
                    self.logger.info("执行信息:{},url为:{}".format(title, detail_link))
                    self.send_data(data)
                    break
            except requests.RequestException as e:
                self.logger.error("访问pdf网络错误:{}".format(detail_link))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问pdf未知的错误:{}".format(detail_link))
                self.logger.exception(e)
        if try_count >= max_retry:
            self.logger.error("{]次重试失败,跳过pdf:{}".format(max_retry, detail_link))
            session.proxies = self.get_proxy()

    def send_data(self, extract_data):
        self.bean_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        pages = self.get_pages(session)
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for page_index in xrange(1, pages):
            url = basic_url.format(page_index)
            try_cnt = 0
            while try_cnt < max_retry:
                try:
                    try_cnt += 1
                    response = self.deal_captcha(url)
                    if response is not None and response.status_code == 200:
                        self.extract_detail_link(response, session, page_index)
                        break
                except requests.RequestException as e:
                    self.logger.error("访问列表页{}网络错误,url:{}".format(page_index, url))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}未知的错误,url:{}".format(page_index, url))
                    self.logger.exception(e)

            if try_cnt >= max_retry:
                self.logger.error("{}次重试失败...跳过第{}页,url:{}".format(max_retry, page_index, url))
                session.proxies = self.get_proxy()

    def get_pages(self, session):
        url = basic_url.format(1)
        try_count = 0
        while try_count < 3:
            try_count += 1
            try:
                response = session.post(url, timeout=timeout)
                if response is not None and response.status_code == 200:
                    pq = PyQuery(response.text, parser="html")
                    page_text = pq.find("div.turn_page").find("script").text()
                    pages = re.findall(r"\d{4,7}", page_text)[0]
                    if pages is not None and pages != "":
                        return int(pages) / 10 + 1
            except requests.RequestException as e:
                self.logger.error("访问页码网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问页码未知的错误")
                self.logger.exception(e)
        return 0

    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def deal_captcha(self, url):
        session = requests.session()
        try:
            resp = session.get(
                "http://61.178.55.5:7080/susong51/cpws_yzm.jpg?n=0",
                timeout=10
            )
            post_data = {
                'priority': 0,
                'captcha_pic': base64.b64encode(resp.content),
                'captcha_type': 'ch_4005',
                'user': 'tangxin',
                'usage': 'gansu_cournt',
            }

            if resp.status_code != 200:
                self.logger.error('访问验证码url失败..')
            result_resp = session.post('http://cs4:5555/captcha', data=post_data)
            if result_resp.status_code != 200:
                self.logger.error('获取验证码识别失败..')

            result = json.loads(result_resp.text)
            report_data = {
                'captcha_type': 'ch_4005',
                'pic_id': result.get("pic_id")
            }

            if result.get('err_no') != 0:
                requests.post(url="http://cs4:5555/report", data=report_data)
                self.logger.error('识别异常: result = {r}'.format(r=json.dumps(result, ensure_ascii=False)))

            captcha = result.get('pic_str')
            check_url = "http://61.178.55.5:7080/susong51/cpws/checkTpyzm.htm"
            params = {"tpyzm": captcha}
            session.post(check_url, params=params)
            resp = session.get(url)
            return resp

        except Exception as e:
            self.logger.error("请求验证码异常")
            self.logger.exception(e)
            return None


if __name__ == "__main__":
    worker = Gansu_zhixing()
    worker()
