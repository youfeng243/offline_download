#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname

PROJECT_PATH = join(dirname(dirname('__file__')),"nbast")

# 启用调试模式
DEBUG = True

# 开启tornado xheaders
XHEADERS = True

# tornado全局配置
TORNADO_CONF = {
	"static_path": "static",
}

# 全局modules配置
COMMON_MODULES = (
	# 'module限定名',

)

#中间件
MIDDLEWARE_CLASSES=(
)

# 路由modules，针对某个路由或某些路由起作用
ROUTE_MODULES = {
	# '路由名称或path正则':['module限定名','!被排除的全局module限定名'],
	# eg: '^/user/login.*$':['utils.modules.LoginModule']
}

LOGGING_DIR = '/var/tmp/'
LOGGING = (
	{
		'name': 'tornado',
		'level': 'INFO',
		'log_to_stderr': False,
		'filename': 'tornado_log.txt'
	},
	{
		'name': 'tornado.application',
		'level': 'INFO',
		'log_to_stderr': True,
		'filename': 'nbast_application_log.txt'
	},
	{
		'name': 'tornado.access',
		'level': 'INFO',
		'log_to_stderr': False,
		'formatter': '%(message)s',
		'filename': 'nbast_access_log.txt'
	},
	{
		'name': 'tornado.general',
		'level': 'INFO',
		'log_to_stderr': False,
		'filename': 'nbast_info_log.txt'
	},
)

# 数据库连接字符串，
# 元祖，每组为n个数据库连接，有且只有一个master，可配与不配slave
DATABASE_CONNECTION = {
	'default': {
		'connections': [
			{
				'ROLE': 'master',
				'DRIVER': 'mysql+mysqldb',
				'UID': 'root',
				'PASSWD': '',
				'HOST': '',
				'PORT': 3306,
				'DATABASE': 'test',
				'QUERY': {"charset": "utf8"}
			},
			{
				'ROLE': 'slave',
				'DRIVER': 'mysql+mysqldb',
				'UID': 'root',
				'PASSWD': '',
				'HOST': '',
				'PORT': 3306,
				'DATABASE': 'test',
				'QUERY': {"charset": "utf8"}
			}]
	}
}

# 每个定时对db进行一次ping操作，防止mysql gone away,设置0为关闭
PING_DB = 300  # (s秒)
# 每次取出ping多少个连接
PING_CONN_COUNT = 5
# sqlalchemy配置，列出部分，可自行根据sqlalchemy文档增加配置项
# 该配置项对所有连接全局共享
SQLALCHEMY_CONFIGURATION = {
	'sqlalchemy.connect_args': {
		# mysqldb connect args
		'connect_timeout': 3
	},
	'sqlalchemy.echo': False,
	'sqlalchemy.max_overflow': 10,
	'sqlalchemy.echo_pool': False,
	'sqlalchemy.pool_timeout': 5,
	'sqlalchemy.encoding': 'utf-8',
	'sqlalchemy.pool_size': 5,
	'sqlalchemy.pool_recycle': 3600,
	'sqlalchemy.poolclass': 'QueuePool'  # 手动指定连接池类
}
