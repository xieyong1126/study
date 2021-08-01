"""
需要指定任务队列！！
"""

# 是一个redis缓存的链接
broker_url='redis://192.168.208.129:6379/3'

# 使用rabbitmq缓存数据库充当任务队列
# broker_url = 'amqp://meihao:123456@172.16.238.128:5672'