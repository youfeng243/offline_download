#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import json
import random
import re
import sys
import requests
from pyquery import PyQuery

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from libs.pdfparser import pdfparser
from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger

check_url = "http://61.178.55.5:7080/susong51/cpws/checkTpyzm.htm"
pdf_url = "http://61.178.55.5:7080/susong51/cpws/downWrit.htm?id={}"
basic_url = "http://61.178.55.5:7080/susong51/fymh/3750/cpws.htm?st=0&q=&ajlb=&wszl=&jbfy=&ay=&ah=&startCprq=&endCprq=&startFbrq=&endFbrq=&page={}"
max_retry = 3
timeout = 40


def get_last_url():
    try:
        f = open("gansu_court.txt")
        return f.read()
    except:
        return ""


class GSCourt(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
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

    def extract_detail_link(self, response, page, last_url, session):
        pq = PyQuery(response.text, parser="html")
        a = pq.find("tr.tr_stripe")
        for i in range(0, len(a)):
            title = a.eq(i).find("a").text()
            title = title.split(".")[0]
            pdf_id = a.eq(i).find("td").eq(1).attr("onclick")
            pdf_id = re.findall(r"'(.+)'", pdf_id)[0]
            if "" != pdf_id:
                self.extract_pdf_link(pdf_id, title, page, i, last_url, session)

    def extract_pdf_link(self, pdf_id, title, page, i, last_url, session):
        pdf_link = pdf_url.format(pdf_id)
        if page == 1 and i == 0:
            with open("gansu_court.txt", "w") as f:
                f.write(pdf_link)
        if pdf_link == last_url:
            self.logger.info("数据没有更新")
            sys.exit()
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(pdf_link)
                if resp is None or resp.status_code != 200:
                    session.proxies = self.get_proxy()
                    continue
                text = pdfparser.pdf2txt(resp.content)
                data = {'case_name': title, 'wenshu_content': text, '_site_record_id': "gansu_court",
                        'source': "gansu_court.py", 'url': pdf_link, "topic": "judgement_wenshu"}
                self.logger.info("案件:{},url为:{}".format(title, pdf_link))
                self.send_data(data)
                break
            except requests.RequestException as e:
                self.logger.error("获取pdf:{}页网络错误".format(pdf_link))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问pdf:{}出现未知的错误".format(pdf_link))
                self.logger.exception(e)
        if try_count >= max_retry:
            self.logger.error("连续{}次访问pdf:{}失败".format(max_retry,pdf_link))

    def send_data(self, extract_data):
        self.beans_client.put("offline_crawl_data", json.dumps(extract_data))

    def start(self):
        last_url = get_last_url()
        session = requests.session()
        session.proxies = self.get_proxy()
        session.headers = self.headers
        pages = self.get_pages()
        if pages < 1:
            self.logger.error("获取页码失败")
            return
        for page in xrange(1, pages):
            url = basic_url.format(page)
            response = self.deal_captcha(url, page)
            if response is None or response.status_code != 200:
                continue
            self.extract_detail_link(response, page, last_url, session)

    def get_pages(self):
        proxy = self.get_proxy()
        url = basic_url.format(1)
        response = self.fetcher.get(url, timeout=timeout, proxies=proxy)
        pq = PyQuery(response.text, parser="html")
        a = pq.find("div.turn_page").find("script").text()
        pages = re.findall(r"\d{5}", a)[0]
        return int(pages) / 20 + 1

    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def deal_captcha(self, url, i):
        session = requests.session()
        try_count = 0
        while try_count < max_retry:
            try_count += 1
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
                params = {"tpyzm": captcha}
                session.post(check_url, params=params)
                resp = session.get(url)
                return resp

            except requests.RequestException as e:
                self.logger.error("获取列表页第{}页网络错误".format(i))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问列表页{}出现未知的错误".format(i))
                self.logger.exception(e)
        self.logger.error("{}次重试访问列表页第{}页失败".format(max_retry,i))
        return None


if __name__ == "__main__":
    worker = GSCourt()
    worker()
