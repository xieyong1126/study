from django.shortcuts import render
from django.views import View
from alipay import AliPay
from django.conf import settings
from django.http import JsonResponse
import os
from orders.models import OrderInfo
from .models import Payment
# Create your views here.


class PaymentStatusView(View):

    def put(self, request):
        # 1、提取支付宝查询字符串参数
        query_string = request.GET # QueryDict
        # {"out_trade_no": xxxxx, "trade_no": xxxxx, "sign": xxxxx}
        query_dict = query_string.dict() # QueryDict.dict()转化成普通字典
        # 获取支付宝签名， 用来验证数据真伪
        signature = query_dict.pop('sign')

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 支付成功之后阿里云回调地址
            app_private_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/app_private_key.pem'
            ),
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/alipay_public_key.pem'
            ),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 2、校验参数是否伪造
        success = alipay.verify(query_dict, signature)
        if success: # 如果返回是True表示支付成功
            # 3、参数无误，写入数据库
            out_trade_no = query_dict.get('out_trade_no') # 美多订单号
            trade_no = query_dict.get('trade_no') # 支付宝流水号/订单号
            # 美多订单关联支付宝订单
            Payment.objects.create(
                order_id=out_trade_no,
                trade_id=trade_no
            )

            order = OrderInfo.objects.get(pk=out_trade_no)
            order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
            order.save()

            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'trade_id': trade_no
            })

        return JsonResponse({'code': 400, 'errmsg': '支付失败！'})


class PaymentView(View):

    def get(self, request, order_id):

        # 1、使用alipay的sdk和阿里交互获取扫码支付页面链接
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None, # 支付成功之后阿里云回调地址
            app_private_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/app_private_key.pem'
            ),
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/alipay_public_key.pem'
            ),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        order = OrderInfo.objects.get(pk=order_id)

        # alipay.api_alipay_trade_app_pay() --> 用于移动端支付链接
        query_string = alipay.api_alipay_trade_page_pay(
            # 付款主题
            subject="美多商城订单：%s"%order_id,
            # 美多商城的订单号
            out_trade_no=str(order_id),
            # 订单付款总价
            total_amount=float(order.total_amount),
            # 重要！return_url指定用户付款成功之后，重定向回美多的链接
            return_url=settings.ALIPAY_RETURN_URL
        )

        # 阿里支付的url是固定的，我们需要在这个url尾部拼接查询字符串
        # 参数，来记录用户的美多商城订单等信息
        alipay_url = settings.ALIPAY_URL + "?" + query_string
        # 2、构建响应返回给用户
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'alipay_url': alipay_url
        })









