#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-15 12:08
import logging

from thrift.protocol.TBinaryProtocol import TBinaryProtocol
from thrift.transport.TTransport import TMemoryBuffer

from bdp.i_crawler.i_downloader.ttypes import DownLoadRsp
from bdp.i_crawler.i_extractor.ttypes import PageParseInfo

THRIFT_OBJ_DEF = {
    "DwonlaodRsp": DownLoadRsp,
    "PageParseInfo": PageParseInfo
}


def thriftobj2bytes(obj):
    """
    convent thrift object instance to string
    :param obj: thrift obj
    :return:  string
    """
    bys = None
    try:
        t_memory_b = TMemoryBuffer()
        t_binaryprotocol_b = TBinaryProtocol(t_memory_b)
        obj.write(t_binaryprotocol_b)
        bys = t_memory_b.getvalue()
    except EOFError, e:
        logging.exception(e.message)
    return bys


def bytes2thriftobj(b_str, class_name):
    """
    convert string to thrift object instance
    :param b_str:
    :param class_name:
    :return: object instance
    """
    obj = None
    try:
        if isinstance(class_name, basestring):
            obj = THRIFT_OBJ_DEF[class_name]()
        elif callable(class_name):
            obj = class_name()
        if obj:
            t_memory_o = TMemoryBuffer(b_str)
            t_binaryprotocol_o = TBinaryProtocol(t_memory_o)
            obj.read(t_binaryprotocol_o)
    except Exception as e:
        logging.exception(e.message)
    return obj
