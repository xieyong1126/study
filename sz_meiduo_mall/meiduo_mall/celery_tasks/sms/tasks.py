'''
当前包封闭异步任务函数
'''
from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.ccp_sms import CCP

@celery_app.task(name='send_sms')
def send_sms(mobile,sms_code):
    result = CCP().send_template_sms(mobile,[sms_code,5],1)

    return result