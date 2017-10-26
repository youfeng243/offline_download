# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ShafaItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    app_name = Field()  # APP名字
    cat = Field()  # APP分类
    comments = Field()  # 评论
    control_type = Field()  # 操作方式
    download_link = Field()  # 下载链接
    downloads = Field()  # 下载次数
    introduction = Field()  # app简介
    language = Field()  # 语言
    package_name = Field()  # 包名
    resolution = Field()  # 分辨率
    score = Field()  # 评分
    system = Field()  # 系统版本
    tag = Field()  # 分类标签
    type = Field()  # 类型
    update = Field()  # 更新
    version = Field()  # 版本
    picture = Field()  # App图片
    package_size = Field()  # 包大小
    mark_distribution = Field()  # 评分分布
    mark_count = Field()  # 评分人数
