#!/usr/bin/env python
# -*- coding:utf-8 -*-

http = "http://"
https = "https://"
backslash = "/"
spot = "."
twoSpotBackslash = "../"
spotBackslash = "./"


def getMainUrl(url):
    """
    从url中抽取出站点主url
    Args:
        url:网站url,必须是绝对url

    Returns: 站点主url

    """
    mainUrl = str(url)
    # 如果以反斜杠开头那么它是一个相对路径，无法抽取主url,直接返回默认值
    if mainUrl.find(backslash) == 0:
        return mainUrl
    # 如果以点开头那么它是一个相对路径，无法抽取主url,直接返回默认值
    if url.find(spot) == 0:
        return mainUrl
    # 如果以http://开头，那么对它进行抽取
    if mainUrl.find(http) == 0:
        host = getHost(mainUrl)
        return http + host
    # 如果以https://开头，那么对它进行抽取
    if mainUrl.find(https) == 0:
        host = getHost(mainUrl)
        return https + host
    return mainUrl


def getHost(url):
    mainUrl = str(url)
    # 如果以反斜杠开头那么它是一个相对路径，无法抽取主url,直接返回默认值
    if mainUrl.find(backslash) == 0:
        return mainUrl
    # 如果以点开头那么它是一个相对路径，无法抽取主url,直接返回默认值
    if url.find(spot) == 0:
        return mainUrl
    startIndex = 0
    endIndex = -1
    # 如果以http://开头，那么对它进行抽取
    if mainUrl.find(http) == 0:
        mainUrl = mainUrl[len(http):len(mainUrl)]
    # 如果以https://开头，那么对它进行抽取
    elif mainUrl.find(https) == 0:
        mainUrl = mainUrl[len(https):len(mainUrl)]
    endIndex = mainUrl.find(backslash)
    if endIndex >= 0:
        mainUrl = mainUrl[startIndex:endIndex]
    return mainUrl


def assembleUrl(srcUrl, newUrl, srcMainUrl=None):
    """
    根据提供的站点主url和祖先srcUrl,把newUrl组装成一个绝对url
    Args:
        srcUrl:newUrl的祖先url
        newUrl:需要组装的url
        srcMainUrl:站点主url

    Returns:

    """
    # 如果以http://开头，那么直接返回不需要组装
    if newUrl.find(http) == 0:
        return newUrl
    # 如果以https://开头，那么直接返回不需要组装
    elif newUrl.find(https) == 0:
        return newUrl
    else:
        mainUrl = ""
        if srcMainUrl != None:
            mainUrl = srcMainUrl
        else:
            mainUrl = getMainUrl(srcUrl)

        resultUrl = newUrl
        index = 0
        head = srcUrl
        # 如果以 / 开头 那么在newUrl前面加上mainUrl
        if newUrl.find(backslash) == 0:
            resultUrl = mainUrl + newUrl
        # 如果以../ 或者../../ 等开头的处理
        elif newUrl.find(twoSpotBackslash) == 0:
            count = 0
            while 1:
                index = newUrl.find(twoSpotBackslash)
                if index != -1:
                    index = index + len(twoSpotBackslash)
                    newUrl = newUrl[index:len(newUrl)]
                    count = count + 1
                else:
                    break
            # 去掉url最后比如 / index.html / index..
            end = head.rindex("/")
            head = head[0:end]
            while count > 0:
                end = head.rindex("/")
                head = head[0:end]
                count = count - 1
            resultUrl = head + "/" + newUrl
        elif newUrl.find(spotBackslash) == 0:
            newUrl = newUrl.replace(spotBackslash, "/")
            resultUrl = head + newUrl
        else:
            end = head.rindex("/")
            head = head[0:end]
            resultUrl = head + "/" + newUrl
    return resultUrl


if __name__ == "__main__":
    url = "http://www.cnblogs.com/mrchige/p/6371783.html"
    mainUrl = getMainUrl(url)
    print mainUrl

    srcUrl = "http://www.cnblogs.com/mrchige/p/6371783.html"
    findUrl = "/test_backslash.html"
    result = "http://www.cnblogs.com/test_backslash.html"
    newUrl = assembleUrl(srcUrl, findUrl)
    print newUrl
    print newUrl == result

    srcUrl = "http://www.cnblogs.com/mrchige/p/6371783.html"
    findUrl = "../test_backslash.html"
    result = "http://www.cnblogs.com/mrchige/test_backslash.html"
    newUrl = assembleUrl(srcUrl, findUrl)
    print newUrl
    print newUrl == result

    srcUrl = "http://www.cnblogs.com/mrchige/p/6371783.html"
    findUrl = "../../test_backslash.html"
    result = "http://www.cnblogs.com/test_backslash.html"
    newUrl = assembleUrl(srcUrl, findUrl)
    print newUrl
    print newUrl == result

    srcUrl = "http://www.cnblogs.com/mrchige/p/6371783.html"
    findUrl = "./test_backslash.html"
    result = "http://www.cnblogs.com/mrchige/p/6371783.html/test_backslash.html"
    newUrl = assembleUrl(srcUrl, findUrl)
    print newUrl
    print newUrl == result

    srcUrl = "http://www.cnblogs.com/mrchige/p/6371783.html"
    findUrl = "test_backslash.html"
    result = "http://www.cnblogs.com/mrchige/p/test_backslash.html"
    newUrl = assembleUrl(srcUrl, findUrl)
    print newUrl
    print newUrl == result
