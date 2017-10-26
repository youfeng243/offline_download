#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-02-21 11:03

from io import BytesIO

bi = BytesIO()
print bi.seekable()
bi.write("fuck")
bi.flush()
bi.seek(0)
bi.write("seek")
x = bi.getvalue()
print x