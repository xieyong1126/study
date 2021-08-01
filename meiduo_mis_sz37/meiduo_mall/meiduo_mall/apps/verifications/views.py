from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.libs.captcha.captcha import captcha
import re,random
# from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import send_sms
import logging
logger = logging.getLogger('django')
# Create your views here.


class ImageCodeView(View):

    def get(self, request, uuid):

        # 1、验证请求参数
        if not re.match(r'^\w{8}(-\w{4}){3}-\w{12}$', uuid):
            return JsonResponse({
                'code': 400,
                'errmsg': 'uuid不符合格式！'
            })

        # 2、调用captcha生成图形验证码
        text, image = captcha.generate_captcha()
        print("图形验证码：", text)
        # 3、验证码存储redis ---> 约定key：img_{uuid}
        # get_redis_connection: 根据django的缓存配置获取一个redis客户端对象
        conn = get_redis_connection('verify_code')
        try:
            conn    .setex(
                "img_%s"%uuid,
                300,
                text
            )
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码保存失败！'
            })


        # 4、把图片返回给前端
        return HttpResponse(image, content_type='image/jpg')






class SMSCodeView(View):

    def get(self, request, mobile):
        # 1、验证前端数据(校验图形验证码)
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')

        # 1.1 如果image_code或者image_code_id某一个不存在，则参数错误
        if not all([image_code, image_code_id]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数错误！'
            })

        # 1.2 读取redis中的图形验证码
        conn = get_redis_connection('verify_code')
        # redis返回的数据，如果没有则None，如果有返回的是字符串的字节形式b'CFGR' --> b'CFGR'.decode() --> 'CFGR'
        image_code_from_redis = conn.get('img_%s'%image_code_id)
        if not image_code_from_redis:
            # 图形验证码过期
            return JsonResponse({
                'code': 400,
                'errmsg': '图形验证码过期！'
            })
        if image_code.lower() != image_code_from_redis.decode().lower():
            # 用户输入错误
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码输入有误！'
            })

        # 为了防止图形验证码被频繁验证，原则上一个图形验证码只能使用一次
        # 解决方案：从redis中读取，就直接销毁
        conn.delete('img_%s'%image_code_id)


        # 判断60秒之内是否发送过短信
        flag = conn.get("sms_flag_%s"%mobile)
        if flag:
           return JsonResponse({
               'code': 400,
               'errmsg': '请勿重复发送短信！'
           })


        # 2、调用云通讯发送短信
        # 2.1 生成一个随机的短信验证码(6位数)
        sms_code = "%06d" % random.randint(0, 999999)
        print("手机验证码：", sms_code)
        # 2.2 短信验证码存储进redis，设计key：sms_{手机号}
        p = conn.pipeline() # 获取一个管道对象
        try:
            p.setex("sms_%s"%mobile, 300, sms_code)
            # 添加标志位
            p.setex("sms_flag_%s"%mobile, 60, '-1')

            p.execute() # 通过管道批量执行redis指令
        except Exception as e:
            logger.info(e)
            return JsonResponse({
                'code': 400,
                'errmsg': 'redis数据库访问失败！'
            })

        # 2.3 调用云通讯发送短信
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 2.3 发布"发送短信"任务，交给异步程序去执行，此处不会阻塞
        send_sms.delay(mobile, sms_code)

        # 3、构建响应返回
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })





















