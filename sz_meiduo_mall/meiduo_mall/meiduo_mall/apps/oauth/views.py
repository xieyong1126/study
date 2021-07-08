from django.shortcuts import render
from django import http
from django.views import View
from django.conf import settings
from django.contrib.auth import login
from django_redis import get_redis_connection

import logging,json,re
from meiduo_mall.apps.oauth.utils import generate_access_token,check_access_token
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.apps.users.models import User
from meiduo_mall.apps.oauth.models import OAuthQQUser
# Create your views here.
logger = logging.getLogger('django')
class QQFristView(View):

    def get(self,request):
        next = request.GET.get('next','/')

        oauth = OAuthQQ(
            client_secret=settings.QQ_CLIENT_SECRET,
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next,
        )
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code':0,
                                  'errmsg':'ok',
                                  'login_url':login_url})


class QQUserView(View):

    def get(self,request):
        code = request.GET.get('code')

        if not code:
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少code'
            })

        #初始化对象
        oauth = OAuthQQ(
                client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state=next
        )
        try:
            token = oauth.get_access_token(code)
            openid = oauth.get_open_id(token)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'认证失败，无法获取用户qq信息'
            })

        try:
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            access_token = generate_access_token(openid)
            return http.JsonResponse({
                'code':300,
                'errmsg':'ok',
                'access_token':access_token
            })
        else:
            user = oauth_qq.user

            login(request,user)
            response = http.JsonResponse({
                'code':0,
                'errmsg':'ok'
            })

            response.set_cookie('username',user.username,max_age=24*12*60*60)
            return response

    def post(self,request):
        #提取参数
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        #校验参数
        if not all([mobile,password,sms_code,access_token]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少参数'
            })

        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.JsonResponse({
                'code':400,
                'errmsg':'手机号格式错误'
            })
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400,
                                 'errmsg': '请输入8-20位的密码'})
        conn = get_redis_connection('verify_code')
        try:
            sms_code_from_redis = conn.get('sms_code_%s'%mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'访问数据失败'
            })

        if sms_code_from_redis is None:
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码失效'
            })
        if sms_code_from_redis.decode() != sms_code:
            return http.JsonResponse({
                'code':400,
                'errmsg':'验证码错误'
            })

        # 调用我们自定义的函数, 检验传入的 access_token 是否正确:
        # 错误提示放在 sms_code_errmsg 位置
        openid = check_access_token(access_token)

        if not openid:
            return http.JsonResponse({
                'code':400,
                'errmsg':'openid错误'
            })

        # 4.保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)

        else:
             # 如果用户存在，检查用户密码
            if not user.check_password(password):
                return http.JsonResponse({
                     'code': 400,
                     'errmsg': '输入的密码不正确'
                })
        # 5.将用户绑定 openid
        try:
            OAuthQQUser.objects.create(openid=openid,user=user)#user_id = user.id
        except Exception as e:
            return http.JsonResponse({
                'code':400,
                'errmsg':'保存用户失败'
            })
        # 6.实现状态保持
        login(request,user)

        response = http.JsonResponse({
            'code':0,
            'errmsg':'ok'
        })

        response.set_cookie('username',user.username,max_age=14*24*60*60)
        return response

