#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  'liusong'
# @Date    '2017/7/15'

import os
import platform
import time
import zipfile
from pyvirtualdisplay import Display
from selenium import webdriver
import stringutils


def get_chrome_proxy_extension(path, proxy):
    """获取一个Chrome代理扩展,里面配置有指定的代理(带用户名密码认证)
    proxy - 指定的代理,格式: username:password@ip:port
    """
    # 存储自定义Chrome代理扩展文件的目录
    CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = os.path.join(path, 'chrome-proxy-extensions')
    # 提取代理的各项参数
    usernameAndPwd = stringutils.substringBefore(proxy, "@")
    username = stringutils.substringBefore(usernameAndPwd, ":")
    password = stringutils.substringAfter(usernameAndPwd, ":")

    ipAndPort = stringutils.substringAfter(proxy, "@")
    ip = stringutils.substringBefore(ipAndPort, ":")
    port = stringutils.substringAfter(ipAndPort, ":")
    # 创建一个定制Chrome代理扩展(zip文件)
    if not os.path.exists(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR):
        os.mkdir(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR)
    extension_file_path = os.path.join(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR, '{}.zip'.format(proxy.replace(':', '_')))
    os.path.exists(extension_file_path) and os.remove(extension_file_path)
    # 扩展文件不存在，创建
    zf = zipfile.ZipFile(extension_file_path, mode='w')
    manifestPath = os.path.join(path, 'manifest.json')
    zf.write(manifestPath, 'manifest.json')
    # 替换模板中的代理参数
    background_content = open(os.path.join(path, 'background.js')).read()
    background_content = background_content.replace('%proxy_host', ip)
    background_content = background_content.replace('%proxy_port', port)
    background_content = background_content.replace('%username', username)
    background_content = background_content.replace('%password', password)
    zf.writestr('background.js', background_content)
    zf.close()
    return extension_file_path


class ChromeSelenium(object):
    def __init__(self, chromedriverPath, intervalTime=0, proxyHost=None, proxyPort=None, proxyConnection=None,
                 proxyUserName=None, proxyPwd=None):
        chrome_options = webdriver.ChromeOptions()
        # 添加一个自定义的代理插件（配置特定的代理，含用户名密码认证）
        if proxyHost is not None and proxyPort is not None:
            if proxyUserName is None:
                chrome_options.add_argument("--proxy-server=" + proxyHost + ":" + str(proxyPort))
            else:
                proxyStr = proxyUserName + ":" + proxyPwd + "@" + proxyHost + ":" + str(proxyPort)
                path = chromedriverPath.replace("/chromedriver", "")
                proxy_extension = get_chrome_proxy_extension(path, proxyStr)
                chrome_options.add_extension(proxy_extension)
        elif proxyConnection is not None:
            proxyStr = proxyConnection
            path = chromedriverPath.replace("/chromedriver", "")
            proxy_extension = get_chrome_proxy_extension(path, proxyStr)
            chrome_options.add_extension(proxy_extension)
        #chrome_options.add_argument("user-data-dir=chrome_user");
        self.display=None
        if platform.platform().find("Linux")!=-1:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        self._driver = webdriver.Chrome(chromedriverPath, chrome_options=chrome_options)
        self.intervalTime = intervalTime
        self.lastDownTime = 0


    def down(self, url,waitLoadTime=1000):
        now = time.time()
        tempIntervalTime = now - self.lastDownTime
        if tempIntervalTime < self.intervalTime:
            time.sleep(tempIntervalTime / 1000)
        self._driver.get(url)
        time.sleep(waitLoadTime/ 1000)
        self.lastDownTime = time.time()

    def getDriver(self,waitLoadXpath=None,waitLoadTime=1000):
        if waitLoadXpath is not None:
            now = time.time()
            while True:
                try:
                    waitLoadElement = self._driver.find_element_by_xpath(waitLoadXpath)
                    if waitLoadElement is not None:
                        break
                    else:
                        alreadyLoadTime = now - time.time()
                        if alreadyLoadTime > waitLoadTime:
                            raise Exception("wait load element[" + waitLoadXpath + "] timeout")
                        else:
                            time.sleep((waitLoadTime - alreadyLoadTime) / 1000)
                except Exception as e:
                    pass
        return self._driver

    def getDriverAndExcludeElement(self,noWaitLoadXpath,waitLoadTime=1000):
        if noWaitLoadXpath is not None:
            now = time.time()
            while True:
                try:
                    waitLoadElement = self._driver.find_element_by_xpath(noWaitLoadXpath)
                    if waitLoadElement is  None:
                        break
                    else:
                        alreadyLoadTime = now - time.time()
                        if alreadyLoadTime > waitLoadTime:
                            raise Exception("wait exclude element[" + noWaitLoadXpath + "] timeout")
                        else:
                            time.sleep((waitLoadTime - alreadyLoadTime) / 1000)
                except Exception as e:
                    pass
        return self._driver

    def getHtml(self, waitLoadXpath=None, waitLoadTime=1000):
        return self.getDriver(waitLoadXpath, waitLoadTime).page_source

    def select(self, select,waitLoadXpath=None,waitLoadTime=1000):
        return self.getDriver(waitLoadXpath,waitLoadTime).find_element_by_csss_selector(select)

    def close(self):
        self._driver.quit()
        if self.display!=None:
            self.display.stop()



if __name__ == "__main__":
    chromedriverPath = "/home/work/webdriver/chromedriver"
    # HDW0OWP3S3E4M8TD:3CC9C9FEB5EF1175@proxy.abuyun.com:9020
    proxyConnection = "HDW0OWP3S3E4M8TD:3CC9C9FEB5EF1175@proxy.abuyun.com:9020"
    downer = ChromeSelenium(chromedriverPath, intervalTime=3000, proxyConnection=proxyConnection)
    downer.down("http://www.baidu.com")
    print  downer.getHtml()
    downer.close()
