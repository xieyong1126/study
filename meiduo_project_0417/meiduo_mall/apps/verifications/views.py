from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
import random, logging

from apps.verifications.libs.captcha.captcha import captcha
from apps.verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code
# Create your views here.


# 创建日志输出器
logger = logging.getLogger('django')


class SMSCodeView(View):
    """短信验证码
    GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
    """

    def get(self, request, mobile):
        """
        实现发送短信验证码的逻辑
        :param mobile: 手机号，如果这个参数在路径中没有串，那么逻辑是无法进入到视图的
        :return: JSON
        """
        # 我们为了尽早的检查出该手机号是否频繁发送短信验证码，所以在逻辑最开始的地方校验
        # 提取出之前给某个手机号绑定的标记
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 判断标记是否存在，如果存在响应错误信息，终止逻辑
        if send_flag:
            return http.JsonResponse({'code': 400, 'errmsg':'频繁发送短信验证码'})

        # 接收参数：mobile(路径参数)、image_code(用户输入的图形验证码)、image_code_id(UUID)
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 校验参数
        # 判断是否缺少必传参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': 400, 'errmsg':'缺少必传参数'})
        # 单个校验参数：image_code(用户输入的图形验证码)、image_code_id(UUID)
        # 说明：短信验证码的逻辑中，不需要对以上参数单独校验
        # 原因：因为image_code和image_code_id可以在对比图形验证码过程中完成校验
        # 如果：image_code和image_code_id有问题，那么图形验证码对比一定不成功

        # 提取图形验证码：以前怎么存，现在怎么提取
        image_code_server = redis_conn.get('img_%s' % uuid)
        # 判断图形验证码是否过期
        if not image_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码失效'})

        # 删除图形验证码：为了变恶意用户恶意的测试该图形验证码，我们要保证每个图形验证码只能使用一次
        redis_conn.delete('img_%s' % uuid)

        # 对比图形验证码：判断用户输入的图形验证码和服务端存储的图形验证码是否一致
        # 先统一类型：将image_code_server由bytes转成str
        # decode()：python提供的，专门将bytes类型的字符串转成str类型的字符串
        image_code_server = image_code_server.decode()
        # 为了提升用户的体验，我们可以将图形验证码的文字，统一大小写，要么统一大写，要么统一小写(OK)
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码有误'})

        # 生成短信验证码：美多商城短信验证码的格式（随机6位数：160116）
        # 如果从0开始，可能随机出来的是个位数或者不满足6位的数字，比如：7，不满足6位数，在前面补0。000007
        random_num = random.randint(0, 999999)
        sms_code = '%06d' % random_num
        logger.info(sms_code)

        # 保存短信验证码：redis的2号库是专门保存图形和短信验证码，也是有300秒的有效期
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # # 发短信时，给该手机号码添加有效期为60秒的标记
        # redis_conn.setex('send_flag_%s' % mobile, 60, 1)

        # 使用pipeline管道来操作redis数据库的数据写入
        # pipeline管道一般用于数据的写入时
        # 创建pipeline管道
        pl = redis_conn.pipeline()
        # 使用管道将请求添加到队列
        pl.setex('sms_%s' % mobile, 300, sms_code)
        # 发短信时，给该手机号码添加有效期为60秒的标记
        pl.setex('send_flag_%s' % mobile, 60, 1)
        # 执行管道：千万不要掉了
        pl.execute()

        # 发送短信验证码：对接容联云通讯的短信SDK
        # 提示:我们不需要判断发短信成功与否，如果失败用户再点击发送即可
        # 该方式是同步发送短信，发短信延迟了，响应也会延迟
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 使用celery的异步任务去发送短信验证码
        # ccp_send_sms_code(mobile, sms_code) # 这个语法还是同步执行函数，不算celery的异步形式

        # 异步函数.delay('参数')：表示代码执行到这儿，该函数不要立即执行，先放行，让下一个代码去执行
        ccp_send_sms_code.delay(mobile, sms_code)

        # 响应结果
        return http.JsonResponse({'code': 0, 'errmsg': '发送短信验证码成功'})


class ImageCodeView(View):
    """图形验证码
    GET http://www.meiduo.site:8000/image_codes/550e8400-e29b-41d4-a716-446655440000/
    """

    def get(self, request, uuid):
        """
        实现图形验证码逻辑
        :param uuid: UUID
        :return: image/jpg
        """
        # 生成图形验证码
        text, image = captcha.generate_captcha()

        # 保存图形验证码
        # 使用配置的redis数据库的别名，创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')
        # 使用连接到redis的对象去操作数据存储到redis
        # redis_conn.set('key', 'value') # 因为没有有效期
        # 图形验证码必须要有有效期的：美多商城的设计是300秒有效期
        # redis_conn.setex('key', '过期时间', 'value')
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 响应图形验证码: image/jpg
        return http.HttpResponse(image, content_type='image/jpg')


