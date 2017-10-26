#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumDowner(object):
    def __init__(self, phantomjsPath,proxyHost=None,proxyPort=None,proxyUserName=None,proxyPwd=None):
        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        desired_capabilities[
            "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        if proxyHost is not None:
            proxy = webdriver.Proxy()
            proxy.socksProxy = proxyHost + ":" + str(proxyPort)
            if proxyUserName is not None:
                proxy.socksUsername = proxyUserName
                proxy.socksPassword = proxyPwd
            proxy.add_to_capabilities(desired_capabilities)
        self._driver = webdriver.PhantomJS(executable_path=phantomjsPath,desired_capabilities=desired_capabilities)


    def down(self, url):
        self._driver.get(url)

    def getDriver(self):
        return self._driver

    def select(self, select):
        return self._driver.find_element_by_csss_selector(select)

    def close(self):
        self._driver.quit()


if __name__ == "__main__":
    downer = None
    try:
        phtantomjsPath = "/Users/liusong/tool/phantomjs-2.1.1-macosx/bin/phantomjs"
        proxyHost = "123.249.16.223"
        proxyPort = 7777
        proxyUserName = "kzp2"
        proxyPwd = "kzp2"
        downer = SeleniumDowner(phtantomjsPath, proxyHost, proxyPort, proxyUserName, proxyPwd)
        url = "http://wenshu.court.gov.cn/Index"
        downer.down(url)
        html = downer.getDriver().execute_script("return document.documentElement.outerHTML")
        print html
        element = downer.getDriver().find_element_by_id("nav")
        element.click()
    except Exception as e:
        print  e
    finally:
        if downer is not None:
            downer.close()
