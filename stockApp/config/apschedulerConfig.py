# -*- coding: utf-8 -*-

'''
scheduer每隔一小时更新一次股票数据
'''
class Config(object):
	JOBS=[
		{
			'id':'job1',
			'func':'App:job1',
			'args':(1,2),
			'trigger':'interval',
			'seconds':3600
			#每小时自动获取一次股票数据
		}
	]
	SCHEDULER_API_ENABLED=True