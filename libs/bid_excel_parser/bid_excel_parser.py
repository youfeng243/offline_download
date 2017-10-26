#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  gikieng.li
# @Date    2017-03-01 16:53

# coding=utf8
# --author:zhangsl
import xlrd
import datetime
import time
import pandas
import sys

sys.path.append('../')
import os

class ExcelParser:
    def __init__(self):
        pass

    def find_table_head(self, table, keyword=u"纳税人识别号"):
        '''通过关键词寻找表头'''
        nrows = table.nrows
        ncols = table.ncols

        head_row = 0
        if nrows != 0:
            for row in range(nrows):
                if keyword in table.row_values(row):
                    find_flag = True
                    head_row = row
                    break
        return head_row

    def fix_merge(self, table, head_row):
        '''将合并单元格全部赋值'''
        merge_map = {}
        for merge in table.merged_cells:
            for row in range(merge[0], merge[1]):
                if row < head_row:
                    continue
                for col in range(merge[2], merge[3]):
                    key = str(row) + "," + str(col)
                    merge_map[key] = table.cell(merge[0], merge[2]).value
        return merge_map

    def find_head_keys(self, table, head_row, merge_map, keyword):
        '''寻找表的字段名'''
        head_keys = []
        last_head_keys = []
        for row in range(table.nrows):
            if row < head_row:
                continue

            if keyword in table.row_values(row):
                head_keys = table.row_values(row)
            else:
                last_head_keys = head_keys
                head_keys = []
                for col in range(table.ncols):
                    if table.cell(row, col).ctype == 6:
                        key = str(row) + "," + str(col)
                        value = merge_map.get(key, "")
                        if value != "":
                            if value in head_keys:
                                head_keys.append(value + "2")
                            else:
                                head_keys.append(value)
                    else:
                        value = table.cell(row, col).value
                        if type(value) == float:
                            value = "%.3f" % value

                        if value != "":
                            if table.cell(row, col).value in head_keys:
                                head_keys.append(value + "2")
                            else:
                                head_keys.append(value)

            if keyword not in head_keys:
                break

        return last_head_keys

    def parser(self, file_name = "",content = None, keyword=u"纳税人识别号"):
        '''excel解析'''
        if not file_name and not content:
            raise Exception("Not content to parser")
        workbook = xlrd.open_workbook(file_name,file_contents=content, formatting_info=True)
        table = workbook.sheets()[0]

        # 1 寻找表头
        head_row = self.find_table_head(table)
        # print head_row

        # 2 寻找合并单元格,并赋值
        merge_map = self.fix_merge(table, head_row)
        # print merge_map

        # 3 寻找表的字段名
        head_keys = self.find_head_keys(table, head_row, merge_map, keyword)

        # 4 开始解析
        result_list = []
        for row in range(table.nrows):
            # 从表头开始解析
            if row < head_row:
                continue

            row_map = {}
            if keyword in table.row_values(row):
                pass
            else:
                for col in range(len(head_keys)):
                    head_key = head_keys[col].strip().replace(' ', '').replace('\t', '').replace('\n', '')
                    if table.cell(row, col).ctype == 6:
                        key = str(row) + "," + str(col)
                        if keyword == merge_map.get(key, ""):
                            row_map = {}
                            break
                        else:
                            value = merge_map.get(key, "")
                            if head_key != "":
                                if isinstance(value, float):
                                    row_map[head_key] = "%.3f" % value
                                else:
                                    row_map[head_key] = value
                    else:
                        if table.cell(row, col).ctype == 3:
                            datetime_value = xlrd.xldate.xldate_as_datetime(table.cell(row, col).value, 0)
                            value = datetime.datetime.strftime(datetime_value, '%Y-%m-%d %H:%M:%S')
                        else:
                            value = table.cell(row, col).value
                        if head_key != "":
                            if isinstance(value, float):
                                row_map[head_key] = "%.3f" % value
                            else:
                                row_map[head_key] = value

            if len(row_map) != 0:
                # 去除空行
                num = 0
                com_value = row_map.values()[0]
                for (key, value) in row_map.items():

                    if value == "" or value == com_value:
                        num += 1

                if float(num) / len(row_map) < 0.25:
                    result_list.append(row_map)

        return result_list

    # ----------------------网页表格解析----------------------------------



if __name__ == "__main__":
    obj = ExcelParser()
    result_list = obj.parser("test.xls",keyword=u"主题")

    for i in result_list:
        for key, value in i.items():
            if isinstance(value, list):
                for i in value:
                    print key, ":", i
            elif isinstance(value, dict):
                for key2, value2 in value.items():
                    print key2, ":", value2
            else:
                print key, ":", value