#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-15 11:34
import json
import time

from bdp.i_crawler.i_downloader.ttypes import DownLoadRsp, DownLoadReq
from bdp.i_crawler.i_extractor.ttypes import PageParseInfo, ExtractInfo, BaseInfo,CrawlInfo
from libs.tools import url_encode, get_url_info


def gen_download_rsp(url, content, parse_extends=None, data_extends=None):
    download_rsp = DownLoadRsp(url=url,
                               redirect_url=url,
                               src_type="develop",
                               content=content,
                               status=0,
                               http_code=200,
                               download_time=time.time(),
                               elapsed=0,
                               page_size=len(content),
                               parse_extends=parse_extends,
                               data_extends=data_extends
                               )
    return download_rsp


def gen_download_req(url, method='get', download_type='simple', post_data=None):
    download_req = DownLoadReq(
        url=url,
        method=method,
        download_type=download_type,
        post_data=post_data
    )
    return download_req


def gen_pageparse_info(url, data, topic_id):
    extract_info = ExtractInfo()
    extract_info.ex_status = 2
    extract_info.topic_id = topic_id
    extract_info.extract_data = json.dumps(data)
    url = url_encode(url)
    url_info = get_url_info(url)
    base_info = BaseInfo(url=url,
                         url_id=url_info.get("url_id"),
                         domain=url_info.get("domain"),
                         domain_id=url_info.get("domain_id"),
                         site=url_info.get("site"),
                         segment_id=url_info.get("segment_id"),
                         site_id=url_info.get("site_id")
                         )
    pinfo = PageParseInfo()
    pinfo.base_info = base_info
    pinfo.extract_info = extract_info
    pinfo.crawl_info = CrawlInfo(download_time=time.time())
    return pinfo
