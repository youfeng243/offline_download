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

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

from sites.common import staticproxy, util
from sites.poc_test.mongo_config import TestDataDB
import logging
from scrapy.selector import Selector
from multiprocessing import Pool

logger = logging.getLogger("tx")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("landchina.log")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

host = "http://www.landchina.com"
basic_url = 'http://www.landchina.com/default.aspx?tabid=261&ComName=default'
MAX_RETRY = 3


# excute_path = "/Users/haizhi/clevertang/phantomjs/bin/phantomjs"


def get_infolist(selector):
    start = 1
    info_list = []
    while True:
        land_id = land_area = land_location = investment = least = ""
        try:
            land_id = selector.xpath(
                "//td[@id='tdContent']/table//tr[3]//div[{}]/table/tbody/tr[1]/td[2]/text()".format(start)).extract()[0]
            land_area = selector.xpath(
                "//td[@id='tdContent']/table//tr[3]//div[{}]/table/tbody/tr[1]/td[4]/text()".format(start)).extract()[0]
            land_location = selector.xpath(
                "//td[@id='tdContent']/table//tr[3]//div[{}]/table/tbody/tr[1]/td[6]/text()".format(start)).extract()[0]
            investment = selector.xpath(
                "//td[@id='tdContent']/table//tr[3]//div[{}]/table/tbody/tr[6]/td[2]/text()".format(start)).extract()[0]
            least = selector.xpath(
                "//td[@id='tdContent']/table//tr[3]//div[{}]/table/tbody/tr[8]/td[2]/text()".format(start)).extract()[0]
        except:
            pass
        finally:
            if not land_id:
                break
            info = {
                'land_id': land_id,
                'land_location': land_location,
                'land_area': land_area,
                'investment': investment,
                'least': least
            }
            info_list.append(info)
            start += 2
    return info_list


def save(title, site, publish_date, info_list, content, source):
    data = {
        'title': title,
        'url': site,
        'publish_date': publish_date,
        'info_list': info_list,
        'content': content,
        "source": source,
        "_id": site
    }
    db_save = pymongo.MongoClient(TestDataDB.MONGODB_SERVER, TestDataDB.MONGODB_PORT)[TestDataDB.MONGODB_DB]
    db_save.authenticate(TestDataDB.MONGO_USER, TestDataDB.MONGO_PSW)
    db_save[TestDataDB.MONGODB_COLLECTION3].save(data)
    logger.info(u"成功保存{}".format(title))


def multi_parse(page_source):
    pool = Pool(8)
    site_list = []
    pq = PyQuery(page_source, parser="html")
    sites = pq.find("table#TAB_contentTable").find("tr")
    for i in xrange(1, len(sites)):
        site = sites.eq(i).find("a").attr("href")
        site = host + site
        site_list.append(site)
    pool.map(parse, site_list)


def parse(site):
    retry = 0
    driver = None
    unique_num = None
    while retry < MAX_RETRY:
        retry += 1
        driver, unique_num = get_phantomjs(site)
        if not driver:
            continue
        break
    if retry >= MAX_RETRY:
        logger.error("访问{}失败".format(site))
        return
    if "JumpSelf()" in driver.page_source:
        driver.find_element_by_xpath("/html/body/div/div[2]/input").click()
        time.sleep(10)
    source = driver.page_source
    close_phantomjs(driver, unique_num)
    selector = Selector(text=source)
    title = selector.xpath("//span[@id='lblTitle']/text()").extract()[0]
    publish_date = selector.xpath("//span[@id='lblCreateDate']/text()").extract()[0]
    content = selector.xpath("//td[@id='tdContent']//text()").extract()
    content = str.join("", content)
    info_list = get_infolist(selector)
    save(title, site, publish_date, info_list, content, source)


all_ip = staticproxy.get_phantom_proxy()


def get_proxy():
    ip = all_ip[random.randint(0, len(all_ip) - 1)]
    logger.info("更换ip为:{}".format(ip))
    return ip


def close_phantomjs(driver, unique_num):
    try:

        driver.quit()
    except Exception as e:
        logger.error("关闭phantomjs失败，需要命令行关闭..")
        logger.exception(e)
        util.run_cmd(
            "ps -ef | grep -i phantomjs | grep -v grep | grep {} | awk '{print $2}' | xargs kill".format(unique_num))
        # finally:
        #     # 删除cookie文件
        #     if os.path.exists(log_path):
        #         os.remove(log_path)


def get_phantomjs(url):
    proxy = get_proxy()
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
        desired_capabilities=desired_capabilities,
        service_args=service_args)
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    try:
        driver.get(url)
        return driver, unique_num
    except Exception as e:
        logger.error("phantomjs访问出错...")
        logger.exception(e)
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


def parse_list(pagenum):
    driver, unique_num = get_phantomjs(basic_url)
    if "JumpSelf()" in driver.page_source:
        driver.find_element_by_xpath("/html/body/div/div[2]/input").click()
        time.sleep(10)
    driver.find_element_by_xpath("//td[@class='pager'][2]/input[1]").clear()
    driver.find_element_by_xpath("//td[@class='pager'][2]/input[1]").send_keys(pagenum)
    driver.find_element_by_xpath("//td[@class='pager'][2]/input[2]").click()
    time.sleep(10)
    return driver.page_source


def main():
    page_num = 100
    for i in xrange(1, page_num):
        retry = 0
        while retry < MAX_RETRY:
            retry += 1
            try:
                page_source = parse_list(i)
                multi_parse(page_source)
                break
            except:
                continue
        if retry > MAX_RETRY:
            logger.error("访问第{}页失败")


if __name__ == "__main__":
    main()
