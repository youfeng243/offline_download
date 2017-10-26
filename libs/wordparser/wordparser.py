#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-22 12:05
import subprocess


class WordparserException(Exception):
    def __init__(self, string):
        Exception.__init__(self, string)

_jar_path_ = "/".join(__file__.split("/")[:-1]) + "/wordparser-1.0.jar"
def word2txt(data, type):
    cmd = " ".join(["java", "-Dfile.encoding=utf-8", "-jar", _jar_path_, type])
    subp = subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    text = subp.communicate(data)[0]
    if subp.returncode != 0:
        raise WordparserException(text)
    return text

if __name__ == "__main__":
    pass