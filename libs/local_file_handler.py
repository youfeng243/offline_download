#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-18 13:36

import os

from conf import m_settings


class LocalFileHandler():
    def __init__(self, task_dir):
        path = os.path.join(m_settings.LOCAL_FILE_BASE_DIR, task_dir)
        if os.path.exists(path):
            if os.path.isdir(path):
                pass
            else:
                raise Exception("exists path but not dir")
        else:
            os.makedirs(path)
        self.path = path

    def get_file(self, filename, mode, **kwargs):
        return open(self.get_file_full_path(filename), mode, **kwargs)

    def check_file_exists(self, filename):
        return os.path.isfile(self.get_file_full_path(filename))

    def get_file_full_path(self, filename):
        filepath = os.path.join(self.path, filename)
        return filepath

