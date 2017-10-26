# !/usr/bin/env python
# encoding: utf-8


import random
import sys

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy

from pyquery import PyQuery

from libs.loghandler import getLogger

from libs.taskbase import TaskBase
import requests, sys

reload(sys)
sys.setdefaultencoding('utf8')

host = "http://www1.sxcredit.gov.cn:8080"
basic_url = "http://www1.sxcredit.gov.cn:8080/WebGovAppSgs/a/WeChatController/xycx"
max_retry = 3
timeout = 40


class SxCredit(TaskBase):
    def __init__(self):
        TaskBase.__init__(self)
        self.resultCount = 0
        # self.fetcher = Fetcher(m_settings.mfile_database())
        self.logger = getLogger(self.__class__.__name__, console_out=False, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常。。。')
        self.params = {
            "pageSize": 20,
            "pageNo": "",
            "dbType": "",
            "keyWord": "1"
        }

    def send_data(self, url, name, date):
        name = name.replace(" ", "")
        extract_data = {
            "topic": "registration_company",
            "company": name,
            "province": "shanxi",
            "city": "",
            "registered_date": date,
            "_site_record_id": "www1.sxcredit.gov.cn",
            "url": url
        }

    def start(self):
        session = requests.session()
        session.headers = self.headers
        session.proxies = self.get_proxy()
        pages = self.get_pages(session)
        if pages < 1:
            return
        for i in xrange(1, pages + 1):
            self.params["pageNo"] = i
            session.params = self.params
            try_cnt = 0
            while try_cnt < max_retry:
                try_cnt += 1
                try:
                    resp = session.post(url=basic_url, timeout=timeout)
                    if resp is None or resp.status_code != 200:
                        session.proxies = self.get_proxy()
                        continue
                    pq = PyQuery(resp.text, parser="html")
                    detail_urls = pq.find("div.weui-cell__bd").find("a")
                    if not isinstance(detail_urls, list) or len(detail_urls) <= 0:
                        self.logger.error("解析列表页第{}页失败".format(i))
                        continue
                    for j in xrange(len(detail_urls)):
                        detail_url = detail_urls.eq(j).attr("href")
                        detail_url = host + detail_url
                        self.parse(detail_url, session)
                    break
                except requests.RequestException as e:
                    self.logger.error("获取列表页第{}页网络错误".format(i))
                    self.logger.exception(e)
                    session.proxies = self.get_proxy()
                except Exception as e:
                    self.logger.error("访问列表页{}出现未知的错误".format(i))
                    self.logger.exception(e)

            if try_cnt >= max_retry:
                self.logger.error("访问列表页第{0}页{1}次重试失败...".format(i, max_retry))
                session.proxies = self.get_proxy()

    def parse(self, url, session):
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                resp = session.get(url=url, timeout=timeout)
                pq = PyQuery(resp.text, parser="html")
                content1 = pq.find("table.sq_tab").eq(0).find("tr")
                dict1 = {}
                for i in xrange(len(content1)):
                    key = content1.eq(i).find("td").eq(0).text().replace("：", "")
                    value = content1.eq(i).find("td").eq(1).text()
                    dict1[key] = value
                dict2 = {}
                content2 = pq.find("table.sq_tab").eq(1).find("tr")
                for j in xrange(len(content2)):
                    key = content2.eq(j).find("td").eq(0).text().replace("：", "")
                    value = content2.eq(j).find("td").eq(1).text()
                    dict2[key] = value
                name = dict1.get(u"企业名称")
                date = dict2.get(u"成立日期")
                self.logger.info("{}:{}".format(name, date))
                self.send_data(url, name, date)
                break
            except requests.RequestException as e:
                self.logger.error("访问详情页网络错误,url为{}".format(url))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问详情页未知的错误,url为{}".format(url))
                self.logger.exception(e)

        if try_count >= max_retry:
            self.logger.error("访问详情页{}次重试失败,url为:".format(max_retry, url))
            session.proxies = self.get_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def get_pages(self, session):
        self.params["page"] = 1
        session.params = self.params
        try_cnt = 0
        while try_cnt < max_retry:
            try:
                try_cnt += 1
                resp = session.post(basic_url)
                if resp is None or resp.status_code != 200:
                    session.proxies = self.get_proxy()
                    continue
                pq = PyQuery(resp.text, parser="html")
                pages = pq.find("ul#pg3").find("li").eq(4).text()
                return int(pages)
            except requests.RequestException as e:
                self.logger.error("访问第一页网络错误")
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问第一页出现未知的错误")
                self.logger.exception(e)
        return 0


if __name__ == "__main__":
    worker = SxCredit()
    worker()
