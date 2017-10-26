#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  six
# @Date    2017-02-24 16:28

from pyquery import PyQuery

import pyqueryutils


def extract(html, extractItems, url=None):
    select = PyQuery(html, parser='html')
    primaryCount = -1
    extractResultMap = {}
    for extractItem in extractItems:
        try:
            extractResult = pyqueryutils.extract(select, extractItem)
        except Exception, e:
            raise Exception("extract path[" + extractItem.name + "] err:" + extractItem.path)
        if 0 == len(extractResult):
            if extractItem.primary or extractItem.mustHaveResult:
                raise Exception("primary path[" + extractItem.name + "] has not result")
            else:
                for i in range(0, primaryCount):
                    extractResult.append("")
        else:
            if extractItem.primary and -1==primaryCount:
                primaryCount = len(extractResult)
        extractResultMap[extractItem.name] = extractResult
    return extractResultMap


def paserTableForOne(html, tableCss):
    if html is None:
        raise Exception("the html must not be None")
    select = PyQuery(html, parser='html')
    tableElements = select.find(tableCss)
    if len(tableElements) > 1:
        raise Exception("the size of select tableElements by path[" + tableCss + "] is more than 1")
    tableElement = tableElements.eq(0)
    resultMap = {}
    trElements = tableElement.find("tr")
    for i in range(0, len(trElements)):
        trElement = trElements.eq(i)
        tdElements = trElement.find("td")
        tdSize = len(tdElements)
        if tdSize > 1:
            j = 0
            while j < tdSize:
                tdElement = tdElements.eq(j)
                key = tdElement.text()
                if key is not None and "" != key:
                    value = ""
                    tempIndex = j + 1
                    if tempIndex < tdSize:
                        tdElement = tdElements.eq(tempIndex)
                        value = tdElement.text()
                    resultMap.put(key, value)
                j += 2;
    return resultMap;


def paserTableForMany(html, tableCss, fieldColumnTrCss, dataTrCss):
    if html is None:
        raise Exception("the html must not be None")
    select = PyQuery(html, parser='html')
    tableElements = select.find(tableCss)
    if len(tableElements) > 1:
        raise Exception("the size of select tableElements by path[" + tableCss + "] is more than 1")
    resultMap = {}
    tableElement = tableElements.eq(0)
    fieldColumnTrElements = tableElement.find(fieldColumnTrCss)
    if 1 != len(fieldColumnTrElements):
        raise Exception("the size of select fieldColumnTrElements by path[" + fieldColumnTrCss + "] is not 1")
    fields = []
    fieldColumnElements = fieldColumnTrElements.find("td")
    for i in xrange(0, len(fieldColumnElements)):
        fieldColumnElement = fieldColumnElements.eq(i)
        field = fieldColumnElement.text()
        fields.append(field)
        resultMap[field] = []
    dataTrElements = tableElement.find(dataTrCss)
    for i in xrange(0, len(dataTrElements)):
        dataTrElement = dataTrElements.eq(i)
        tdElements = dataTrElement.find("td")
        for j in xrange(0, len(tdElements)):
            tdElement = tdElements.eq(j)
            result = tdElement.text()
            resultMap[fields[j]].append(result)
    return resultMap


if __name__ == "__main__":
    print "哈喽"
