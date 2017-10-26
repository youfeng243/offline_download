#!/usr/bin/env python
# coding=utf8

import sys

import requests

sys.path.append('../')
sys.path.append('../..')
sys.path.append('../../..')
from libs.thrift_utils.thrift_object_generator import gen_download_req
from libs.thrift_utils.thrift_serialize import thriftobj2bytes
from conf import m_settings
from libs.taskbase import TaskBase
from pyquery import PyQuery as pq
from libs.loghandler import getLogger


class HeNanBid(TaskBase):
    def __init__(self):
        super(HeNanBid, self).__init__()
        self.logger = getLogger(self.__class__.__name__, console_out=True, level="debug")

    def get_detail_page(self):
        try:
            session = requests.session()
            zhaobiao_url = 'http://www.hnsztb.com.cn/zbxx/zbgg.asp?page=3'
            zhaobiao_content = session.get(url=zhaobiao_url).content.decode('gb2312')
            zhaobiao_total_page = int(
                zhaobiao_content.split('页</option></select></td></tr></table></td>')[0].split('\'>第')[-1])
            for i in range(1, zhaobiao_total_page + 1):
                try:
                    url = 'http://www.hnsztb.com.cn/zbxx/zbgg.asp?page={0}'.format(i)
                    content = session.get(url=url).content
                    content = content.decode('gb2312', 'ignore')
                    result = pq(content, parser='html')
                    hrefs = result.find('span').find('a')
                    for j in range(0, len(hrefs)):
                        url = 'http://www.hnsztb.com.cn/zbxx/' + hrefs.eq(j).attr('href')
                        self.put_bean(url=url)
                        print url
                except Exception, e:
                    print e.message

            zhongbiao_url = 'http://www.hnsztb.com.cn/zbxx/zhbgg.asp?page=1'
            zhongbiao_content = session.get(url=zhongbiao_url).content.decode('gb2312')
            zhongbiao_total_page = int(
                zhongbiao_content.split('页</option></select></td></tr></table></td>')[0].split('\'>第')[-1])
            for i in range(1, zhongbiao_total_page + 1):
                try:
                    url = 'http://www.hnsztb.com.cn/zbxx/zhbgg.asp?page={0}'.format(i)
                    content = session.get(url=url).content
                    content = content.decode('gb2312', 'ignore')
                    result = pq(content, parser='html')
                    hrefs = result.find('td.style1').find('a')
                    for j in range(0, len(hrefs)):
                        url = 'http://www.hnsztb.com.cn/zbxx/' + hrefs.eq(j).attr('href')
                        self.put_bean(url=url)
                        print url
                except Exception, e:
                    print e.message
        except Exception, e:
            print e.message

    def put_bean(self, url):
        try:
            self.logger.info(url)
            obj = gen_download_req(url, download_type='phantom')
            self.beanstalkclient = m_settings.beanstalk_client2()
            self.output_tube = m_settings.BEANSTALKD_TUBE.get('download_req')
            self.beanstalkclient.put(self.output_tube, thriftobj2bytes(obj))
        except Exception as e:
            self.logger.error(str(e))


if __name__ == "__main__":
    crawler = HeNanBid()
    crawler.get_detail_page()
