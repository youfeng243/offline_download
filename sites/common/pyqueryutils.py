#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  six
# @Date    2017-02-24 16:28

import stringutils


class ExtractItem(object):
    def __init__(self, name, primary, mustHaveResult,
                 path, attName, containsText=None,
                 substringStart=None, substringEnd=None,
                 startWith=None, endWith=None,
                 neadReplaceText=None, replaceText=None):
        self.name = name
        self.primary = primary
        self.mustHaveResult = mustHaveResult
        self.path = path
        self.attName = attName
        self.containsText = containsText
        self.substringStart = substringStart
        self.substringEnd = substringEnd
        self.startWith = startWith
        self.endWith = endWith
        self.neadReplaceText = neadReplaceText
        self.replaceText = replaceText


def extract(pyquery, extractItem):
    """
    基于pyquery抽取结果
    :param pyquery: pyquery
    :param extractItem: 需要抽取的项
    :return: 返回抽取结果
    """
    findElements = pyquery.find(extractItem.path)
    size = len(findElements)
    results = []
    if size > 0:
        for i in range(0, size):
            result = ""
            findElement = findElements.eq(i)
            if "text" == extractItem.attName:
                result = findElement.text()
            else:
                result = findElement.attr(extractItem.attName)
            isAdd = True
            if extractItem.containsText is not None and "" != extractItem.containsText:
                if result.find(extractItem.containsText) == -1:
                    isAdd = False
            if extractItem.startWith is not None and "" != extractItem.startWith:
                if result.find(extractItem.startWith) != 0:
                    isAdd = False
            if extractItem.endWith is not None and "" != extractItem.endWith:
                if result.find(extractItem.endWith) + len(extractItem.endWith) != len(result):
                    isAdd = False
            if isAdd:
                if extractItem.neadReplaceText is not None and "" != extractItem.neadReplaceText:
                    result=result.replace(extractItem.neadReplaceText,extractItem.replaceText)

                if extractItem.substringStart is not None and extractItem.substringEnd is None:
                    result= stringutils.substringAfter(result, extractItem.substringStart)
                elif extractItem.substringStart is None and extractItem.substringEnd is not None:
                    result = stringutils.substringBefore(result, extractItem.substringEnd)
                elif extractItem.substringStart is not None and extractItem.substringEnd is not None:
                    result = stringutils.substringBetween(result, extractItem.substringStart, extractItem.substringEnd)
                if result!="" and result.strip()!="":
                    results.append(result)
    return results

