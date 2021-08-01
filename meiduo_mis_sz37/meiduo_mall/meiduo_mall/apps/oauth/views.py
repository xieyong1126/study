from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings

from .models import OAuthQQUser
from users.models import User
from oauth.utils import generate_access_token,check_access_token
import json,re
from django_redis import get_redis_connection
from django.contrib.auth import login
from carts.utils import merge_cart_cookie_to_redis
# Create your views here.


# 登陆页面链接获取
class QQFirstView(View):

    def get(self, request):

        # 1、提取前端传参数next
        next = request.GET.get('next')

        # 2、使用QQLoginTool工具获取扫码页面链接
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            # 用户完成整个qq登陆流程之后，返回到美多到哪个页面
            state=next,  # http://www.meiduo.site:8080/
        )
        qq_login_url = oauth.get_qq_url()

        # 3、构建响应数据返回
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'login_url': qq_login_url
        })




class QQUserView(View):

    def get(self, request):

        # 1、提取code
        code = request.GET.get('code')

        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            # 用户完成整个qq登陆流程之后，返回到美多到哪个页面
            state=next,  # http://www.meiduo.site:8080/
        )

        try:
            # 2、根据code获取AccessToken
            access_token = oauth.get_access_token(code)
            # 3、根据AccessToken获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return JsonResponse({
                'code': 400,
                'errmsg': '用户code无效！'
            })

        # 4、获取openid仅仅代表用户qq身份没有问题；
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist as e:
            # 用户没有绑定，返回加密后对openid —— 前端让用户数据用户名和密码，后续接口再去判断绑定
            token = generate_access_token(openid)
            return JsonResponse({
                'code': 400,
                'errmsg': '未绑定',
                'access_token': token
            })
        else:
            # 如果用户已经绑定了qq，说明用户已经注册过了"美多用户
            login(request, qq_user.user)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', qq_user.user.username)
            return merge_cart_cookie_to_redis(request, qq_user.user, response)



    def post(self, request):
        # 把美多账号和qq进行绑定

        # 1、提取前端传值
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        # 2、校验
        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({'code': 400, 'errmsg': '参数缺失！'})

        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '请输入正确的手机号码'})

        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'errmsg': '请输入8-20位的密码'})


        conn = get_redis_connection('verify_code')
        sms_code_from_redis = conn.get('sms_%s'%mobile)
        if not sms_code_from_redis:
            return JsonResponse({'code': 400, 'errmsg': '手机验证码过期！'})

        if sms_code != sms_code_from_redis.decode():
            return JsonResponse({'code': 400, 'errmsg': '验证码有误'})

        openid = check_access_token(access_token)
        if openid is None:
            return JsonResponse({'code': 400, 'errmsg': 'token无效！'})

        # 3、判断用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist as e:
            # 3.1 不存在新建在绑定
            user = User.objects.create_user(
                username=mobile,
                mobile=mobile,
                password=password
            )

            try:
                OAuthQQUser.objects.create(
                    user=user,
                    # user_id=user.id
                    openid=openid
                )
            except Exception as e:
                return JsonResponse({'code': 400, 'errmsg': '用户绑定失败！'})

        else:
            # 3.2 存在直接绑定
            if not user.check_password(password):
                return JsonResponse({'code':400, 'errmsg': '用户名或密码错误！'})

            try:
                OAuthQQUser.objects.create(
                    user=user,
                    # user_id=user.id
                    openid=openid
                )
            except Exception as e:
                return JsonResponse({'code': 400, 'errmsg': '用户绑定失败！'})


        # 4 构建响应返回
        login(request, user)
        response =  JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username)
        return merge_cart_cookie_to_redis(request, user, response)

















