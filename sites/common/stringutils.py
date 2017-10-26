#!/usr/bin/env python
# -*- coding:utf-8 -*-




def substringBetween(text, open, close):
    if text is None and open is None and close is None:
        return None
    start = text.find(open)
    if -1 != start:
        fromIndex = start + len(open.decode('utf-8'))
        end = text.find(close, fromIndex, len(text));
        if -1 != end:
            return text[fromIndex: end]
    return None

def substringBefore(text,separator):
    if text is None and separator is None:
        return None
    end = text.find(separator)
    if -1 != end:
        return text[0: end]
    return None

def substringAfter(text, separator):
    if text is None and separator is None :
        return None
    start = text.find(separator)
    if -1 != start:
        start = start + len(separator.decode('utf-8'))
        return text[start:len(text)]
    return None


if __name__ == "__main__":
    text = "var pageNum = 1;var totalPage = 319;var totalRecords = 7973;"
    open = "totalRecords"
    close = "7973"
    answer = " = "
    result = substringBetween(text, open, close)
    print "正确结果:" + answer
    print "截取结果:" + result
    print answer == result

    text = "var pageNum = 1;var totalPage = 319;var totalRecords = 7973;"
    separator = "totalRecords"
    answer = "var pageNum = 1;var totalPage = 319;var "
    result = substringBefore(text, separator)
    print "正确结果:" + answer
    print "截取结果:" + result
    print answer == result

    text = "var pageNum = 1;var totalPage = 319;var totalRecords = 7973;"
    separator = "totalRecords"
    answer = " = 7973;"
    result = substringAfter(text, separator)
    print "正确结果:" + answer
    print "截取结果:" + result
    print answer == result
