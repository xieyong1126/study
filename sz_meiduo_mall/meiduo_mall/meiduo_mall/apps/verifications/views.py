from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection

from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from meiduo_mall.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms
import logging,random
logger = logging.getLogger('django')

# Create your views here.
class ImageCodeView(View):
    def get(self,request,uuid):
        text,image = captcha.generate_captcha()
        conn = get_redis_connection('verify_code')
        print('图片验证码：',text)
        try:
            conn.setex('img_%s'%uuid,300,text)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码保存失败'
            })
        return http.HttpResponse(image,content_type='image/jpg')

class SMSCodeView(View):
    def get(self,request,mobile):
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')
        conn = get_redis_connection('verify_code')

        if not all([image_code,image_code_id]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少参数'
            })
        try:
            code_from_redis = conn.get('img_%s'%image_code_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'访问数据库失败'
            })
        print('验证码：',code_from_redis)
        if not code_from_redis:
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码失效'
            })
        if code_from_redis.decode().lower() != image_code.lower():
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码错误'
            })
        conn.delete('img_%s'%image_code_id)

        try:
            mobile_flag = conn.get(mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code :400,'
                'errmsg':'访问数据库失败'
            })
        if mobile_flag:
            return http.JsonResponse({
                'code':400,
                'errmsg':'请勿频繁发送验证码'
            })
        #CCP().send_template_sms('13037129714', ['习大大发来贺电', 5], 1)
        sms_code = '%06d'%random.randint(0,999999)
        print(sms_code)

        p = conn.pipeline()
        try:
            p.setex('sms_code_%s'%mobile,300,sms_code)
            p.setex(mobile,60,1)
            p.execute()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'保存验证码失败'
            })
        # CCP().send_template_sms(mobile,[sms_code,5],1)
        send_sms.delay(mobile,sms_code)

        return http.JsonResponse({
            'code':0,
            'errmsg':'ok'
        })


