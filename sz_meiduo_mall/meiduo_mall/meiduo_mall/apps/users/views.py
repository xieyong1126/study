from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.apps.users.models import User
from django_redis import get_redis_connection
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from meiduo_mall.utils.view import login_required,LoginRequiredMixin
from celery_tasks.email.tasks import send_verify_email
import json,re
from .models import User
import logging
logger = logging.getLogger('django')

# Create your views here.

class UsernameCountView(View):
    def get(self,request,username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'访问数据库失败'
            })
        return http.JsonResponse({
            'code':0,
            'errmsg':'ok',
            'count':count
        })

class MobileCountView(View):
    def get(self,request,mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'访问数据失败'
            })
        return http.JsonResponse({
            'code':0,
            'errmsg':'ok',
            'count':count
        })


class RegisterView(View):

    def post(self,request):

        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        allow = data.get('allow')

        # 1.1 必传字段校验
        if not all([username,password,password2,mobile,sms_code]):
            return http.JsonResponse({
                'code':400,
                'errmsg':'参数有误！'
            })

        # 1.2 用户名校验
        if not re.match(r'^[a-zA-Z-9_-]{5,20}$',username):
            return http.JsonResponse({
                'code': 400,
                'errmsg': "用户名有误！"
            })
        if re.match(r'^[0-9]{5,20}$',password):

            return http.JsonResponse({
                'code':400,
                'eermsg':'用户名不能为纯数字'
            })

        # 1.3 密码校验
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return http.JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误！'
            })
        if password != password2:
            return http.JsonResponse({
                'code': 400,
                'errmsg': '两次输入密码不匹配！'
            })

            # 1.4 手机号验证
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({
                'code': 400,
                'errmsg': '手机格式有误！'
            })

            # 1.5 短信验证码校验
        if not re.match(r'\d{6}', sms_code):
            return http.JsonResponse({
                'code': 400,
                'errmsg': '手机验证码有误！'
            })

            # 1.6 allow字段校验
        if not isinstance(allow, bool):
            return http.JsonResponse({
                'code': 400,
                'errmsg': 'allow字段有误！'
            })

            # 1.7 确定用户是否勾选协议
        if allow != True:
            return http.JsonResponse({
                'code': 400,
                'errmsg': '请同意用户协议！'
            })

            # 1.8 短信验证码比对
        conn = get_redis_connection('verify_code')
        sms_code_from_redis = conn.get('sms_code_%s' % mobile)
        if not sms_code_from_redis:
            return http.JsonResponse({
                'code': 400,
                'errmsg': '验证码过期！'
            })

        if sms_code != sms_code_from_redis.decode():
            return http.JsonResponse({
                'code': 400,
                'errmsg': '短信验证码错误！'
            })

        # 2、新建用户模型类对象，保存数据库
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            return http.JsonResponse({
                'code': 400,
                'errmsg': '写入数据库失败！'
            })
        # 4、使用session记录用户登陆信息
        # request.session['username'] = user.username
        login(request, user)  # login帮助我们把用户数据写入session缓存中

        # 5、构建响应
        response = http.JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response


class LoginView(View):

    def post(self, request):
        # 1、数据校验
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 1.1 必传校验
        if not all([username, password]):
            return http.JsonResponse({
                'code': 400,
                'errmsg': '参数有误！'
            })
        # 1.2 用户名校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({
                'code': 400,
                'errmsg': "用户名有误！"
            })

        # 1.3 密码校验
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return http.JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误！'
            })

        # 1.4 校验remembered字段
        if not isinstance(remembered, bool):
            return http.JsonResponse({
                'code': 400,
                'errmsg': "remembered参数有误！"
            })
        # 2、判断用户名和密码（传统的身份认证）
        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist as e:
        #     # 用户名未找到对应的用户
        #     return JsonResponse({'code': 400, 'errmsg': '用户不存在！'})
        #
        # if not user.check_password(password):
        #     return JsonResponse({'code': 400, 'errmsg': '密码有误！'})

        # 校验成功返回用户对象，校验失败返回None
        user = authenticate(request, username=username, password=password)
        if not user:
            return http.JsonResponse({'code': 400, 'errmsg': '用户名或密码有误！'})

        # 3、判断是否需要记住用户登陆状态,用户数据写入session(redis缓存)
        login(request, user)
        if remembered:
            request.session.set_expiry(None)  # 默认保存2周
        else:
            request.session.set_expiry(0)  # 浏览器关闭清楚session,删除redis中记录的用户缓存数据

        response = http.JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })

        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response


class LogoutView(View):

    def delete(self, request):
        # 1、清除用户登陆session数据
        # 首先根据request.COOKIES中的sessionid,在根据sessionid查找到缓存中的用户数据，然后删除
        logout(request)
        # 2、删除cookie数据
        response = http.JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        response.delete_cookie('username')
        return response


# from django.utils.decorators import method_decorator
class UserInfoView(LoginRequiredMixin, View):

    # 装饰器使用方案一：
    # @method_decorator(login_required)
    def get(self, request):
        # request.user是一个根据session数据，验证出来的用户对西那个，如果没有session数据则是一个匿名用户对象！

        # 1、必须验证用户登陆
        # request.user.is_authenticated，用户模型类对象该属性为True
        # request.user.is_anonymous, 匿名用户该属性为True

        # if not request.user.is_authenticated:
        #     # 未登陆
        #     return JsonResponse({
        #         'code': 400,
        #         'errmsg': '未登陆！'
        #     })


        # 2、提取用户数据，构建响应返回
        return http.JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': request.user.username,
                'mobile': request.user.mobile,
                'email': request.user.email,
                'email_active':request.user.email_active
            }
        })


class EmailView(LoginRequiredMixin,View):
    def put(self,request):

        email = json.loads(request.body.decode()).get('email')
        if not email:
            return http.JsonResponse({
                'code':'400',
                'errmsg':'缺少email参数'
            })
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({
                'code':400,
                'errmsg':'参数email有误'
            })
        # 赋值 email 字段
        try:
            request.user.email=email
            request.user.save()
        except EmailView as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'添加邮箱失败'
            })

        verify_url = request.user.generate_verify_email_url()
        send_verify_email.delay(email, verify_url)

        return http.JsonResponse({
            'code':0,
            'errmsg':'ok'
        })

class VerifyEmailView(View):

    def put(self,request):

        token = request.GET.get('token')
        if not token:
            return http.JsonResponse({
                'code':400,
                'errmsg':'缺少参数token'
            })

        user = User.check_verify_email_token(token)
        if not user:
            return http.JsonResponse({
                'code':400,
                'errmsg':'无效的token'
            })

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code':400,
                'errmsg':'激活失败'
            })

        return http.JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })



