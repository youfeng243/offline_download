#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import json
import random
import sys

import requests
import xlrd
from pyquery import PyQuery
import time

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy
from libs.packet_parser_info import packet
from libs.pybeanstalkd import thrift2bytes
from conf import m_settings
from libs.fetcher import Fetcher
from libs.taskbase import TaskBase
from libs.loghandler import getLogger

captcha_url = "http://epub.sipo.gov.cn/vci.jpg"
Host = "epub.sipo.gov.cn"
Origin = "http://epub.sipo.gov.cn"
base_url = "http://epub.sipo.gov.cn/patentoutline.action"
max_retry = 8
timeout = 60
CRAWL_URL = 'http://epub.sipo.gov.cn/haizhi/patent_xml/'


class Patent(TaskBase):
    def __init__(self, keyword_file):
        TaskBase.__init__(self)
        self.resultCount = 0
        self.fetcher = Fetcher(m_settings.mfile_database())
        self.beans_client = m_settings.beanstalk_client()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "yunsuo_session_verify=3cd1cbcc50fcc7370f2a2763c75bb068; WEB=20111116; _va_ref=%5B%22%22%2C%22%22%2C1502952231%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D4bjc9rHU7-vnw0b8RZpDANpyfJ1225ATP_sfN1RmLPFNj0lxkGPJeXnjAqhYQnyw%26wd%3D%26eqid%3Da9e16f9000005b53000000065992af8c%22%5D; _va_id=351cb7f7a4789198.1500605762.10.1502952231.1502952231.; _gscu_2029180466=00605765wexn3w10; _gscbrs_2029180466=1; _gscbrs_1718069323=1; _gscu_1718069323=0060576102po0287; JSESSIONID=E2636AE520A20FED544DF051D246A2EF; _gscu_884396235=009648437t9s0r30; _gscs_884396235=t02957973tx632d14|pv:18; _gscbrs_884396235=1; Hm_lvt_06635991e58cd892f536626ef17b3348=1501226357,1501740816,1501839021,1502934925; Hm_lpvt_06635991e58cd892f536626ef17b3348=1502963931; _gscs_7281245=t029579737i1b8z14|pv:18; _gscbrs_7281245=1; _gscu_7281245=00964844hfvhr030",
            # "Content-Length": "345",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Referer": base_url,
            "Origin": Origin,
            "Host": Host,
        }
        self.all_ip = staticproxy.get_all_proxie()
        if not isinstance(self.all_ip, list) or len(self.all_ip) <= 0:
            raise Exception('代理初始化异常……')
        self.post_data = {
            "showType": "1",
            "numSortMethod": "4",
            "strLicenseCode": "",
            "strSources": "pip",
            "Submit": "继续",
            "numIp": "",
            "numIpc": "",
            "numIg": "",
            "numIgc": "",
            "numIgd": "",
            "numUg": "",
            "numUgc": "",
            "numUgd": "",
            "numDg": "",
            "numDgc": "",
            "pageSize": "10",
        }
        self.pageNow = "{page}"
        self.strWhere = "PA,IN,AGC,AGT+='%{keyword}%' or PAA,TI,ABH+='{keyword}'"

        self.keyword_file = keyword_file
        self.keyword_list = None
        self.get_keyword_list()

    def start(self):
        for keyword in self.keyword_list:
            self.post_data['strWhere'] = self.strWhere.format(keyword=keyword)
            pages = self.get_pages()
            if pages < 1:
                self.logger.error("获取页码失败")
                return
            for page in xrange(1, pages + 1):
                response = self.if_captcha(base_url, page)
                if response is None or response.status_code != 200:
                    continue
                self.parse(response, keyword, page)

    def get_keyword_list(self):
        if 'xlsx' in self.keyword_file:
            try:
                data = xlrd.open_workbook(self.keyword_file)
                table = data.sheets()[0]
                self.keyword_list = table.col_values(0)[1:]
                return self.keyword_list
            except:
                self.logger.error('打开文件失败，请检查……')
        else:
            self.keyword_list = self.keyword_file

    def get_pages(self):
        response = self.if_captcha(base_url, 1)
        if response is None:
            self.logger.error('请求首页失败，重新发起请求')
            response = self.if_captcha(base_url, 1)

        pq = PyQuery(response.content, parser="html")
        pages = pq.find(".next").find("a").eq(-2).text()
        if not pages:
            pages = 1
        return int(pages)

    def get_proxy(self):
        all_ip = self.all_ip
        ip = all_ip[random.randint(0, len(all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def parse(self, response, keyword=None, page=None):
        self.logger.info('数据抓取成功，正在解析数据……')

        pq = PyQuery(response.content, parser="html")
        patent = pq.find('.cp_box').items()
        for ear_item in patent:
            patent_data = {}
            title = ear_item.find('h1').text().split(']')[1]
            patent_type = ear_item.find('h1').text().split(']')[0].replace('[', '')
            patent_data['title'] = title
            patent_data['patent_type'] = patent_type

            li_items = ear_item.find('li').items()
            for li in li_items:
                text = li.text()  # 申请公布号：CN103157141A
                if not text:
                    continue
                try:
                    field = text.split('：')[1]  # CN103157141A
                except IndexError:
                    if '/' in text and '(' in text and ')' in text:
                        continue
                    self.logger.error('异常字段<{0}>，请检查'.format(text))
                if '申请公布号' in text:
                    patent_data['publish_no'] = field
                elif '申请公布日' in text:
                    patent_data['query_info'] = field
                elif '申请号' in text:
                    patent_data['submit_id'] = field
                elif '申请日' in text:
                    patent_data['submit_date'] = field
                elif '申请人' in text:
                    patent_data['submitter'] = field
                elif '发明人' in text:
                    patent_data['inventors'] = field.split(';')
                elif '地址' in text:
                    patent_data['address'] = field
                elif '分类号' in text:
                    patent_data['category'] = field.split('专利代理机构')[0].replace('全部', '')
                    hidden_items = li.find('div').find('ul').find('li').items()
                    for hidden_li in hidden_items:
                        text = hidden_li.text()  # 专利代理机构：西安西达专利代理有限责任公司61202
                        if not text:
                            continue
                        try:
                            field = text.split('：')[1]  # 西安西达专利代理有限责任公司61202
                        except IndexError:
                            if '/' in text and '(' in text and ')' in text:
                                continue
                            self.logger.error('异常字段<{0}>，请检查'.format(text))
                        if '专利代理机构' in text:
                            patent_data['agent_org'] = field
                        elif '代理人' in text:
                            patent_data['agents'] = field.split(';')

            abstract = ear_item.find('.cp_jsh').text().replace('摘要：', '').replace('全部', '')
            patent_data['abstract'] = abstract

            patent_data['_site_record_id'] = patent_data['publish_no']
            patent_data['url'] = '{0}id={1}'.format(CRAWL_URL, patent_data['publish_no'])

            self.send_data(patent_data)
        else:
            self.logger.warning('{keyword}在第{page}页无专利数据，无需解析……'.format(keyword=keyword, page=page))
            return
        self.logger.info('本页数据解析完成，已发往消息队列……')

    def send_data(self, extract_data):
        topic_id = m_settings.TOPICS.get('patent')
        url = extract_data.get('url')

        self.beans_client.put(m_settings.BEANSTALKD_TUBE['extract_info'],
                              thrift2bytes(packet(topic_id, url, extract_data)))

    def deal_captcha(self, url, i):
        self.post_data['pageNow'] = self.pageNow.format(page=i)
        session = requests.session()
        try_count = 0
        while try_count < max_retry:
            try_count += 1
            try:
                # response = session.get(url, data=self.post_data)
                # pq = PyQuery(response.content, parser="html")
                # vci_img = pq.find("#vci").attr("src")
                # captcha_url = urlutils.assembleUrl(base_url, vci_img)
                resp = session.get(
                    captcha_url,
                    timeout=timeout
                )
                post_data = {
                    'priority': 0,
                    'captcha_pic': base64.b64encode(resp.content),
                    'captcha_type': 'ch_4005',
                    'user': 'czc',
                    'usage': 'patent',
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
                    session.post(url="http://cs4:5555/report", data=report_data)
                    self.logger.error('识别异常: result = {r}'.format(r=json.dumps(result, ensure_ascii=False)))

                captcha = result.get('pic_str')
                if len(captcha) != 5:
                    return self.deal_captcha(url, i)
                params = {
                    "vct": captcha,
                    # "numIg": "0",
                    # "numIp": "0",
                    # "numIpc": "0",
                    # "numIgd": "0",
                    # "numUg": "0",
                }
                proxy = self.get_proxy()
                session.proxies = proxy

                self.post_data.update(params)
                res = session.post(url, data=self.post_data)
                return res

            except requests.RequestException as e:
                self.logger.error("获取列表页第{}页网络错误".format(i))
                self.logger.exception(e)
                session.proxies = self.get_proxy()
            except Exception as e:
                self.logger.error("访问列表页{}出现未知的错误".format(i))
                self.logger.exception(e)
        self.logger.error("{}次重试访问列表页第{}页失败".format(max_retry, i))
        return None

    def if_captcha(self, url, i, retries=max_retry):
        response = self.deal_captcha(url, i)
        if response is None:
            self.logger.warning('连接失败达到最大重试次数,继续尝试……')
            time.sleep(20)
            return self.if_captcha(url, i, retries)
        while True:
            if '近期异常访问较多' not in response.content:
                break
            if retries == 0:
                self.logger.warning('访问验证码已达到最大次数，请检查后再继续重试')
                return

            retries -= 1
            self.logger.info('第{0}次验证码破解失败，继续尝试……'.format(max_retry - retries))
            time.sleep(20)
            return self.if_captcha(url, i, retries)

        return response


if __name__ == "__main__":
    # file_name = ['发明公布', '发明授权', '实用新型', '外观设计']
    file_name = '20170819广东农信2000家名单.xlsx'
    # file_name = ['海致网络']
    worker = Patent(file_name)
    worker()
