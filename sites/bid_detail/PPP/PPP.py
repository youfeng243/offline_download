#!/usr/bin/env python
# encoding: utf-8

import random
import re
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from sites.common import staticproxy

from pyquery import PyQuery

from libs.fetcher import Fetcher
from libs.loghandler import getLogger
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes

from conf import m_settings
from libs.taskbase import TaskBase
import requests

reload(sys)
sys.setdefaultencoding('utf8')

host = "http://www.chinappp.cn/Project/"
basic_url = "http://www.chinappp.cn/Project/Project{}List.html?page={}"
max_retry = 3
timeout = 40


class PPP(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.province = ""
        self.city = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')

    def send_data(self, url, project, industry, location, investment_amount, term_of_cooperation,
                  project_operation_mode,
                  reward_mechanism, launch_time, launch_type, project_overview, contacts, contact_phone,
                  demonstration_project_level,
                  demonstration_project_batch, ppp_implementation_phase, content, amounts):
        extract_data = {
            "_site_record_id": "www.chinappp.cn",
            "project": project,
            "province": "",
            "industry": industry,
            "location": location,
            "investment_amount": investment_amount,
            "term_of_cooperation": term_of_cooperation,
            "project_operation_mode": project_operation_mode,
            "reward_mechanism": reward_mechanism,
            "launch_time": launch_time,
            "launch_type": launch_type,
            "project_overview": project_overview,
            "contacts": contacts,
            "contact_phone": contact_phone,
            "demonstration_project_level": demonstration_project_level,
            "demonstration_project_batch": demonstration_project_batch,
            "ppp_implementation_phase": ppp_implementation_phase,
            "content": content,
            "city": "",
            "district": "",
            "project_id": "",
            "amounts": amounts,
            "units": "元",
            "project_type": ""
        }

        self.beans_client.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                              thrift2bytes(packet(100, url, extract_data)))

    def start(self):
        for a in ["", "fgw"]:
            session = requests.session()
            session.headers = self.headers
            session.proxies = self.get_proxy()
            pages = self.get_pages(a, session)
            if pages < 1:
                self.logger.error("获取页码失败")
                return
            for j in range(1, pages):
                url = basic_url.format(a, j)
                try_cnt = 0
                while try_cnt < max_retry:
                    try_cnt += 1
                    try:
                        resp = session.get(url, timeout=timeout)
                        if resp is not None and resp.status_code == 200:
                            pq = PyQuery(resp.text, parser="html")
                            notes = pq.find("span.project_title")
                            for i in xrange(0, len(notes)):
                                detail_url = notes.eq(i).find("a").attr("href")
                                real_url = host + detail_url
                                self.parse_content(real_url, session)
                            break
                    except requests.RequestException as e:
                        self.logger.error("获取列表页第{}页网络错误,url为:{}".format(i, url))
                        self.logger.exception(e)
                        session.proxies = self.get_proxy()
                    except Exception as e:
                        self.logger.error("访问列表页{}出现未知的错误,url为:{}".format(i, url))
                        self.logger.exception(e)
                if try_cnt >= max_retry:
                    self.logger.error("{}次重试访问列表页{}失败,url为:{}...".format(max_retry, i, url))
                    session.proxies = self.get_proxy()

    def get_pages(self, a, session):
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.get(url=basic_url.format(a, 1), timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    detail_pq_result = PyQuery(resp.content, parser='html')
                    page = detail_pq_result.find("ul.pagination").find("a").eq(14).attr("href")
                    pages = re.findall(r"\d+", page)
                    return int(pages[0])
                session.proxies = self.get_proxy()
            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def parse_content(self, url, session):
        count = 0
        while count < max_retry:
            count += 1
            try:
                resp = session.get(url, timeout=timeout)
                if resp is not None and resp.status_code == 200:
                    pq = PyQuery(resp.content, parser="html")
                    project = pq.find("h4.investment_title").text()
                    ppp_text = pq.find("div.investment_show").find("span").text()
                    investment_amount = ppp_text.split()[1]
                    if "亿" in investment_amount:
                        investment_amount = str(float(investment_amount.split("亿")[0]) * 10000) + "万元"

                    amounts = investment_amount
                    ppp_implementation_phase = ppp_text.split()[5]
                    project_overview = pq.find("div.investment_info3").find("div").text()
                    content = project_overview
                    notes = pq.find("div.investment_info").find("li")
                    location = notes.eq(0).text().split("：")[1]
                    industry = notes.eq(1).text().split("：")[1]
                    term_of_cooperation = notes.eq(2).text().split("：")[1]
                    project_operation_mode = notes.eq(3).text().split("：")[1]
                    reward_mechanism = notes.eq(4).text().split("：")[1]
                    launch_time = notes.eq(5).text().split("：")[1]
                    launch_type = notes.eq(6).text().split("：")[1]
                    contacts = notes.eq(7).text().split("：")[1]
                    contact_phone = notes.eq(8).text().split("：")[1]
                    demonstration_project_level = notes.eq(9).text().split("：")[1]
                    demonstration_project_batch = notes.eq(10).text().split("：")[1]
                    self.send_data(url, project, industry, location, investment_amount, term_of_cooperation,
                                   project_operation_mode,
                                   reward_mechanism, launch_time, launch_type, project_overview, contacts,
                                   contact_phone,
                                   demonstration_project_level,
                                   demonstration_project_batch, ppp_implementation_phase, content, amounts)
                    self.logger.info("成功获取{}详情".format(project))
                    break
            except requests.RequestException as e:
                self.logger.error("访问详情页网络错误,url为{}".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页未知的错误,url为{}".format(url))
                self.logger.exception(e)
        if count >= max_retry:
            self.logger.error("{}次重试访问详情页{}失败...".format(max_retry, url))
            session.proxies = self.get_proxy()


if __name__ == "__main__":
    worker = PPP()
    worker()
