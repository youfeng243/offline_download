#!/usr/bin/env python
# encoding: utf-8
import random

import sys
from pyquery import PyQuery
sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
from conf import m_settings
from libs.loghandler import getLogger
from libs.pybeanstalk import PyBeanstalk
from libs.taskbase import TaskBase
from libs.thrift_utils import thrift_object_generator, thrift_serialize
from sites.common import staticproxy
from tx_session import proxy_session


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
        self.beanstalk = PyBeanstalk(m_settings.BEANSTALKD.get('host'), m_settings.BEANSTALKD.get('port'))
        self.output_tube = m_settings.BEANSTALKD_TUBE.get('download_req')
        self.topic_id = 32  # judgement_wenshu,裁判文书
        self.post_data = {
            "__VIEWSTATE": "/wEPDwUKLTg0MDU2NDIyMw9kFgJmD2QWAgICD2QWBGYPFgIeCWlubmVyaHRtbAU4PGEgaHJlZj0nL0xvZ2luLmFzcHgnIHN0eWxlPSdkaXNwbGF5Om5vbmUnPuivt+eZu+W9lTwvYT5kAgIPZBYEZg8WAh4LXyFJdGVtQ291bnQCChYUZg9kFgJmDxUFJGRkMmJhOWFmLThmM2MtNDViYi05YmQ4LTcyMzhhMmQxNmJiMAQwOTAxDOiNlOWfjuazlemZoirmnY7njonmmI7kuqTpgJrogofkuovkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCAQ9kFgJmDxUFJDgzOGNjYzA5LTVhN2UtNDQyZC1hZTliLTEwZDUyY2NjMjE3OQQwOTAxDOiNlOWfjuazlemZoirlvKDlnaTlhpvljbHpmanpqb7pqbbkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCAg9kFgJmDxUFJDM3MmJmMDI3LWI3YjItNDA5My1hNDA3LWNkYTE2YjFjZTljMQQwOTAxDOiNlOWfjuazlemZoirosKLngavmmI7lvIDorr7otYzlnLrkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCAw9kFgJmDxUFJGY2MjgwNTQ4LWI3MjktNDEyNy1iZWUyLTViNzY0MGIyODIwNQQwOTAxDOiNlOWfjuazlemZoirnjovlv5fnq4vljbHpmanpqb7pqbbkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCBA9kFgJmDxUFJDI0YTJiMjc2LTMxNTItNGMwZi05YTlkLTNmOGU4OTdlYmYwNwQwOTAxDOi/nuWfjuazlemZokLosKLku4HmlozpnZ7ms5XmjIHmnInjgIHnp4Hol4/mnqrmlK/jgIHlvLnoja/kuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCBQ9kFgJmDxUFJDIxNjUxNDc0LWYxOTktNGNiMS05ZDYyLWMzMjkyMThiMmY3YwQwOTAxDOi/nuWfjuazlemZoirmsaDmma/ovonpnZ7ms5Xnu4/okKXkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCBg9kFgJmDxUFJGExYzI5ZDUyLTk1NTQtNGE5OS1hNTQ2LWNiMGQzNGZjNmRlMgQwOTAxDOi/nuWfjuazlemZojbpu4Tku5XovonjgIHpmYjnpaXng73kuqTpgJrogofkuovkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCBw9kFgJmDxUFJGU4ZGFkNjAyLTlmN2QtNDFiNy05YzgwLWFlODM5MGVmMTZlNgQwOTAxDOi/nuWfjuazlemZoirpu4Tph5Hpk63ljbHpmanpqb7pqbbkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCCA9kFgJmDxUFJDY4MjM4ZThmLTY1OGEtNDNhZi1hYTA0LTk3YjY3MjRkMGE0NwQwOTAxDOi/nuWfjuazlemZoirpgrHpgInmlofljbHpmanpqb7pqbbkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCCQ9kFgJmDxUFJDgxZGUzMWJkLWRlNGUtNDFmNi1iOTA5LWFmZGYxOTg2YzU1OQQwOTAxDOi/nuWfjuazlemZoirkuKXmib/puY/ljbHpmanpqb7pqbbkuIDlrqHliJHkuovliKTlhrPkuaYKMjAxNy0wOS0yOGQCAQ8PFgIeC1JlY29yZGNvdW50Av3yCmRkZBroQ8MyDzBov4mO+tSxNmTpolmt7xvnvEQFKH0k0ZDZ",
            "__VIEWSTATEGENERATOR": "D65BE68E",
            "__EVENTTARGET": "ctl00$cplContent$AspNetPager1",
            "__EVENTARGUMENT": 2,
            "ctl00$cplContent$AspNetPager1_input": 1

        }

    all_ip = staticproxy.get_phantom_proxy()

    def get_proxy(self):
        ip = self.all_ip[random.randint(0, len(self.all_ip) - 1)]
        self.logger.info("更换ip为:{}".format(ip))
        return ip

    def parse_list(self, i, j):
        url = BASE_URL.format(i + 1)
        session = proxy_session()
        resp = session.post(url=url, data=self.post_data)
        pq = PyQuery(resp.text, parser="html")
        self.post_data["__VIEWSTATE"] = pq.find("input#__VIEWSTATE").attr("value")
        self.post_data["ctl00$cplContent$AspNetPager1_input"] = j + 1
        self.post_data["__EVENTARGUMENT"] = j + 2
        sites = pq.find("ul.module-case-items").find("a")
        for i in xrange(0, len(sites)):
            site = sites.eq(i).attr("href")
            site = HOST + site
            # print site
            self.put_bean(site)

    def start(self):
        for i in xrange(0, 5):
            pages = page_list[i]
            for j in xrange(1, pages):
                retry = 0
                while retry < MAX_RETRY:
                    retry += 1
                    try:
                        self.parse_list(i, j)
                        break
                    except Exception as e:
                        continue
                if retry > MAX_RETRY:
                    self.logger.error("访问第{}页失败")

    def put_bean(self, url):

        # pdb.set_trace()
        obj = thrift_object_generator.gen_download_req(url)
        self.logger.info('put beanstalk url:%s topic_id:%d' % (url, self.topic_id))
        self.beanstalk.put(self.output_tube, thrift_serialize.thriftobj2bytes(obj))


if __name__ == "__main__":
    worker = fjcourt()
    worker()
