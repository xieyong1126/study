from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from django.contrib.auth import login
import json, re
from django_redis import get_redis_connection

from apps.oauth.models import OAuthQQUser
from apps.oauth.utils import generate_access_token_openid, check_access_token_openid
from apps.users.models import User
# Create your views here.


class QQUserView(View):
    """处理授权后的回调
    GET /oauth_callback/
    """

    def get(self, request):
        """处理授权后的回调逻辑"""
        # 获取code
        code = request.GET.get('code')
        if not code:
            return http.JsonResponse({'code': 400, 'errmsg': '缺少code'})

        # 创建SDK的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)
            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': 'OAuth2.0认证失败'})

        # 使用openid去判断当前的QQ用户是否已经绑定过美多商城的用户（纯属美多商城自己的需求，跟OAuth2.0无关）
        try:
            oauth_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid未绑定美多商城的用户：将用户引导到绑定用户的页面
            # 重要提示：工作中，会规定很多的状态码，而每个状态码都对应一种操作结果
            # 提示：在美多商城里面如果QQ用户未绑定美多商城的用户，通过状态码300告诉前端，让他根据需求文档做响应的处理
            # 提示：为了简单处理，我们将openid还给用户自己保存，将来在绑定用户时，前端再传给我们即可
            access_token_openid = generate_access_token_openid(openid)
            return http.JsonResponse({'code': 300, 'errmsg': '用户未绑定的', 'access_token': access_token_openid})
        else:
            # openid已绑定美多商城的用户：直接实现状态保持即可
            # 提示：在实现QQ登录时，真正登录到美多商城的不是QQ用户，而是QQ用户绑定的美多商城用户
            # login(request=request, user='跟openid绑定的美多商城的用户对象')
            login(request=request, user=oauth_model.user)

            response = http.JsonResponse({'code': 0, 'errmsg': 'OK'})
            response.set_cookie('username', oauth_model.user.username, max_age=3600*24*14)

            # 合并购物车
            from apps.carts.utils import merge_cart_cookie_to_redis
            response = merge_cart_cookie_to_redis(request, oauth_model.user, response)

            return response

    def post(self, request):
        """实现openid绑定用户的逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')
        sms_code_client = json_dict.get('sms_code')
        access_token = json_dict.get('access_token')

        # 校验参数
        if not all([mobile, password, sms_code_client, access_token]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '参数password有误'})
        # 校验短信验证码
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile) # sms_code_server是bytes
        # 判断短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码失效'})
        # 对比用户输入的和服务端存储的短信验证码是否一致
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})
        # 校验openid
        openid = check_access_token_openid(access_token)
        if not openid:
            return http.JsonResponse({'code': 400, 'errmsg': '参数openid有误'})

        # 判断手机号对应的用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果手机号对应的用户不存在，新建用户:这个时候新建的用户，手机号即是用户名，也是手机号
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 如果手机号对应的用户已存在，校验密码
            if not user.check_password(password):
                return http.JsonResponse({'code': 400, 'errmsg': '密码有误'})

        # 将上面得到的用户跟openid进行绑定即可
        # create_user()：只有继承自AbstractUser的用户模型类才能去调用的，创建用户记录
        # create()：凡是继承自Model的模型类都可以调用，用来创建记录
        try:
            OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            return http.JsonResponse({'code': 400, 'errmsg': 'QQ登录失败'})

        # 实现状态保持
        login(request=request, user=user)
        response = http.JsonResponse({'code': 0, 'errmsg': 'OK'})
        response.set_cookie('username', user.username, max_age=3600*24*14)

        # 合并购物车
        from apps.carts.utils import merge_cart_cookie_to_redis
        response = merge_cart_cookie_to_redis(request, user, response)

        # 响应结果
        return response


class QQURLView(View):
    """QQ登录扫码链接
    GET /qq/authorization/
    """

    def get(self, request):
        """提供QQ登录扫码链接"""
        # 接收next参数
        next = request.GET.get('next', '/')

        # 创建OAuthQQ对象
        # oauth = OAuthQQ(client_id='101474184',
        #                 client_secret='c6ce949e04e12ecc909ae6a8b09b637c',
        #                 redirect_uri='http://www.meiduo.site:8080/oauth_callback.html',
        #                 state=next)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        # 调用提供QQ登录扫码链接的接口函数
        login_url = oauth.get_qq_url()

        # 响应结果
        return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'login_url': login_url})

