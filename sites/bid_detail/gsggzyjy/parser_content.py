#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-25 17:31
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
from libs.pdfparser import pdfparser


def deal(data):
    extract_data = None
    try:
        text = pdfparser.pdf2txt(data['data'])
        extract_data = {}
        extract_data['title'] = data['title']
        extract_data['content'] = text
        extract_data['publish_time'] = data['publish_time']
        extract_data['doc_id'] = data['sourceUrl']
        extract_data['_site_record_id'] = data['sourceUrl']
    except Exception as e:
        extract_data = None

    return extract_data


def dealTakeText(data, text):
    extract_data = None
    try:
        extract_data = {}
        extract_data['title'] = data['title']
        extract_data['content'] = text
        extract_data['publish_time'] = data['publish_time']
        extract_data['doc_id'] = data['sourceUrl']
        extract_data['_site_record_id'] = data['sourceUrl']
    except Exception as e:
        extract_data = None

    return extract_data
