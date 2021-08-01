"""
该模块，用于构建celery程序对象，并加载配置和加载任务函数
"""
import os
# 异步任务执行程序(消费者程序)，运行之初执行加载django配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

from celery import Celery
# 1、新建一个celery应用程序对象
celery_app = Celery("meiduo_mall")

# 2、加载配置信息(指定任务队列)
celery_app.config_from_object('celery_tasks.config')

# 3、加载任务(celery中，任务是需要被封装成一个包文件的！)
celery_app.autodiscover_tasks([
    'celery_tasks.sms',
    'celery_tasks.email',
    'celery_tasks.html',
])