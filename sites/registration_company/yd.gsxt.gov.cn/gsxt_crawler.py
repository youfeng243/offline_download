# -*- coding:UTF-8 -*-

# !/usr/bin/env python
import json
import random
import sys

import pymongo
import requests

sys.path.append("..")
sys.path.append("../..")
reload(sys)
sys.setdefaultencoding('utf8')


class Gsxt():
    def __init__(self):
        pass

    def start(self):
        db_save = pymongo.MongoClient('172.16.215.2', 40042)['schedule_data']
        db_save.authenticate('work', 'haizhi')
        file=open('./test.txt')
        proxy_list=[]
        proxy_file=open('./proxy.txt')
        for line in proxy_file:
            proxy_list.append(line.strip())
        while True:
            for line in file:
                keyword=line.strip()
                page = 1
                keyword=str("甘肃")+str(keyword)
                while True:
                    url = "http://yd.gsxt.gov.cn/QuerySummary"
                    try:
                        session = requests.session()
                        data = "mobileAction=entSearch&keywords={0}&topic=1&pageNum={1}&pageSize=10&userID=id001&userIP=192.123.123.22".format(
                            keyword, page)
                        content=session.get(url='http://172.18.180.225:9300/proxy/test11111').content
                        proxy = {'http': 'http://' + content}
                        session.proxies=proxy
                        session.headers = {
                            "Host": "yd.gsxt.gov.cn",
                            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "Origin": "file://",
                            "Connection": "keep-alive",
                            "Accept": "*/*",
                            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403 Html5Plus/1.0",
                            "Content-Length": "133",
                        }
                        content = session.post(url=url, data=data,timeout=10).content
                        if content =="[]":
                            print keyword,'noresult'
                            break
                        result=json.loads(content)
                        for element in result:
                            name=str(element['ENTNAME']).replace('<font color=red>','').replace('</font>','')
                            print keyword,name,"success****"
                            data = {
                                "_id": name,
                                "source":"gsxt"
                            }
                            db_save['gansu_all_names'].save(data)
                        # print proxy,"avaiable"
                        if len(result)!=50:
                            break
                        print keyword,'success'
                        page+=1
                    except Exception, e:
                        pass
                        print e.message


if __name__ == "__main__":
    worker = Gsxt()
    worker.start()