#!/usr/bin/env python
# encoding: utf-8
import os
import random

import pymongo
import time

import sys
from pyquery import PyQuery
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from common.pybeanstalkd import PyBeanstalk
from common.taskbase import TaskBase
from common.thrift_utils import thrift_object_generator, thrift_serialize
from common.tools import str_obj
from conf import settings
from conf.settings import phantomjs_path

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from common.loghandler import getLogger
from sites.utils import staticproxy, util

page_list = [17809, 54841, 7185, 23358, 19, 209]
BASE_URL = 'http://www.fjcourt.gov.cn/page/public/RefereeclericalMore.aspx?cate=090{}'
HOST = "http://www.fjcourt.gov.cn"
MAX_RETRY = 5
TIMEOUT = 60
PAGES = 400


# excute_path = "/Users/haizhi/clevertang/phantomjs/bin/phantomjs"
class fjcourt(TaskBase):
    def __init__(self):
        super(fjcourt, self).__init__()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")
        self.session = None
        self.session_id = None
        self.beanstalk = PyBeanstalk(settings.BEANSTALKD.get('host'), settings.BEANSTALKD.get('port'))
        self.output_tube = settings.BEANSTALKD_TUBE.get('download_req')
        self.topic_id = 32  # judgement_wenshu,裁判文书

    def multi_parse(self, page_source):
        pq = PyQuery(page_source, parser="html")
        sites = pq.find("ul.module-case-items").find("a")
        for i in xrange(0, len(sites)):
            site = sites.eq(i).attr("href")
            site = HOST + site
            print site
            self.put_bean(site)

    all_ip = staticproxy.get_phantom_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def close_phantomjs(self, driver, unique_num):
        try:

            driver.quit()
        except Exception as e:
            self.logger.error("关闭phantomjs失败，需要命令行关闭..")
            self.logger.exception(e)
            util.run_cmd(
                "ps -ef | grep -i phantomjs | grep -v grep | grep {} | awk '{print $2}' | xargs kill".format(
                    unique_num))
            # finally:
            #     # 删除cookie文件
            #     if os.path.exists(log_path):
            #         os.remove(log_path)

    def get_phantomjs(self,url):
        proxy = self.get_proxy()
        proxy = proxy.get("http")
        from datetime import datetime
        now_time = datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前的时间
        random_num = random.randint(0, 1000)  # 生成随机数n,其中0<=n<=100
        if random_num <= 100:
            random_num = str(0) + str(random_num)
        unique_num = str(now_time) + str(random_num)
        log_path = os.path.join(os.getcwd(), "log", "{}.txt".format(unique_num))
        proxy = proxy[7:]
        proxy_auth = None
        proxy_list = proxy.split("@")
        if len(proxy_list) >= 2:
            proxy = proxy_list[1]
            proxy_auth = proxy_list[0]
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',

        }
        service_args = ['--proxy={}'.format(proxy),
                        '--proxy-type=http',
                        '--load-images=no',
                        '--disk-cache=no',
                        '--ignore-ssl-errors=true',
                        '--cookies-file={}'.format(log_path)

                        ]
        if proxy_auth is not None:
            service_args.append("--proxy-auth={}".format(proxy_auth))
        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        for key, value in headers.iteritems():
            desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value
        driver = webdriver.PhantomJS(
            desired_capabilities=desired_capabilities
            )
        driver.implicitly_wait(30)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        try:
            driver.get(url)
            return driver, unique_num
        except Exception as e:
            self.logger.error("phantomjs访问出错...")
            self.logger.exception(e)
            driver.execute_script('window.stop()')
            driver.quit()
            return None
            # finally:
            #     try:
            #         driver.quit()
            #     except Exception as e:
            #         logger.error("关闭phantomjs失败，需要命令行关闭..")
            #         logger.exception(e)
            #         util.run_cmd(
            #             "ps -ef | grep -i phantomjs | grep -v grep | grep {} | awk '{print $2}' | xargs kill".format(
            #                 unique_num))
            #     finally:
            #         # 删除cookie文件
            #         if os.path.exists(log_path):
            #             os.remove(log_path)

    def parse_list(self, sb, pagenum):
        driver, unique_num = self.get_phantomjs(BASE_URL.format(sb + 1))
        driver.find_element_by_xpath("//input[@id='ctl00$cplContent$AspNetPager1_input']").clear()
        driver.find_element_by_xpath("//input[@id='ctl00$cplContent$AspNetPager1_input']").send_keys(str(pagenum))
        driver.find_element_by_xpath("//input[@id='ctl00$cplContent$AspNetPager1_btn']").click()
        time.sleep(3)
        source = driver.page_source
        self.close_phantomjs(driver, unique_num)
        return source

    def start(self):
        for i in xrange(0, 5):
            pages = page_list[i]
            for j in xrange(1, pages):
                retry = 0
                while retry < MAX_RETRY:
                    retry += 1
                    try:
                        page_source = self.parse_list(i, j)
                        self.multi_parse(page_source)
                        break
                    except Exception as e:
                        continue
                if retry > MAX_RETRY:
                    self.logger.error("访问第{}页失败")

    def put_bean(self, url):

        # pdb.set_trace()
        obj = thrift_object_generator.gen_download_req(url)
        self.logger.info('put beanstalk output_tube:%s topic_id:%d' % (self.output_tube, self.topic_id))
        self.beanstalk.put(self.output_tube, thrift_serialize.thriftobj2bytes(obj))


if __name__ == "__main__":
    worker = fjcourt()
    worker()
