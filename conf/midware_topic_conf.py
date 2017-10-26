#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 数据中间件配置文件
import os
import sys

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
reload(sys)

path = os.path.abspath(sys.argv[0]).split('mfiledownload/')[0]
logfile = {
    'beanstalk_consumer.logs': path + 'mfiledownload/logs/beanstalk_consumer.logs',
    'tmp.logs': path + 'mfiledownload/logs/tmp.logs',
    'data_transaction.logs': path + 'mfiledownload/logs/data_transaction.logs',
    'test.logs': path + 'mfiledownload/logs/test.logs',
}
handled_flag = 1
handling_flag = 0

beanstalk_host_cs2 = 'cs2'
beanstalk_port = 11300
beanstalk_tube = 'offline_crawl_data'
mongodb_app_data = {
    'host': '172.16.215.16',
    'port': 40042,
    'name': 'app_data',
    'username': 'work',
    'password': 'haizhi'
}

mongodb_schedule_data = {
    'host': '172.16.215.2',
    'port': 40042,
    'name': 'schedule_data',
    'username': 'work',
    'password': 'haizhi'
}

IMCOMPLETE_DATA = False
COMPLETE_DATA = True

# 系统字段以及主题 每个主题必须带上这些字段
sys_conf = {
    "url": "",  # 抓取url
    "topic": "",  # 数据是属于什么主题 如 招中标
    "source": "",  # 来源 数据来自哪个脚本,
    "_site_record_id": ""  # 站点的host
}
topic = [
    "bid_detail",
    "registration_company",
    "baidu_news",
    "judgement_wenshu"
]

bid_detail = {
    "topic": "bid_detail",  # 数据是属于什么主题 如 招中标
    "url": "",  # 抓取url
    "title": "",  # 标题
    "content": "",  # 正文信息
    "source": "",  # 来源 数据来自哪个脚本
    "province": "",  # 发布省份
    "city": "",  # 发布城市
    "publish_time": "",  # 发布时间 页面上能抽取则抽取
}

registration_company = {
    "type": "object",
    "title": "新注册企业列表",
    "properties": {
        "company": {
            "type": "string",
            "title": "企业名称"
        },
        "province": {
            "type": "string",
            "title": "省份"
        },
        "city": {
            "type": "string",
            "title": "城市"
        },
        "registered_date": {
            "type": "string",
            "title": "注册日期"
        }
    }
}

baidu_news = {
    "type": "object",
    "title": "百度新闻",
    "properties": {
        "title": {
            "type": "string",
            "title": "新闻标题"
        },
        "summary": {
            "type": "string",
            "title": "正文"
        },
        "url": {
            "type": "string",
            "title": "新闻链接"
        },
        "_site_record_id": {
            "type": "string",
            "title": "站点host"
        },
        "topic": {
            "type": "string",
            "title": "站点主题(即为字段对象的名称)"
        },
        "source": {
            "type": "string",
            "title": "数据来源 来自哪个脚本"
        },
        "publish_time": {
            "type": "string",
            "title": "新闻发布时间(如果能格式化处理则处理为1999-09-09 11:11:11这种格式)"
        }

    }
}

judgement_wenshu = {
    "type": "object",
    "title": "裁判文书",
    "properties": {
        "url": {
            "type": "string",
            "title": "文书链接"
        },
        "_site_record_id": {
            "type": "string",
            "title": "站点host"
        },
        "topic": {
            "type": "string",
            "title": "站点主题(即为字段对象的名称)"
        }
        ,
        "source": {
            "type": "string",
            "title": "数据来源 来自哪个脚本"
        },
        "wenshu_content": {
            "type": "string",
            "title": "文书正文"
        },
        "case_name": {
            "type": "string",
            "title": "案件名"
        }

    }
}

# table列表
table_list = [
    "judgement_wenshu"
]

# 设置表的主键和索引
judgement_wenshu_index = {

}

table_duplicate_flag = {
    'judgement_wenshu': ['case_name', 'url'],
    'registration_company': ['company'],
    'shixin_info': ['case_id'],
    'zhixing_info': ['case_id']
}

winserver_table_duplicate_flag = {
    'judgement_wenshu': ['case_name', 'PageUrl'],
    'news': ['summary','PageUrl'],
    'baidu_news': ['summary','PageUrl'],
    'bid_detail': ['PageUrl', 'title']
}
