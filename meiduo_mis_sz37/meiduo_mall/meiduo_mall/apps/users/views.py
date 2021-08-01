from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import User
from django.conf import settings
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.view import LoginRequiredMixin
from goods.models import SKU,GoodsVisitCount
from carts.utils import merge_cart_cookie_to_redis
from django.utils import timezone

import logging
logger = logging.getLogger('django')
# Create your views here.


class UserBrowseHistory(LoginRequiredMixin, View):


    def get(self, request):
        # 1、提取当前登陆用户的redis历史访问记录
        conn = get_redis_connection('history')

        # [b'3', b'5', b'8', b'14', b'13']
        history_list = conn.lrange('history_%s'%request.user.id, 0, -1)

        # 2、查找所有的sku商品
        skus = []
        for sku_id in history_list:
            # sku_id: b'3'

            try:
                sku = SKU.objects.get(pk=int(sku_id))

                # 如果商品下架，那么不给用户返回该条浏览记录
                if not sku.is_launched:
                    raise SKU.DoesNotExist()

            except SKU.DoesNotExist as e:
                continue # 当前sku_id的sku商品不存在或下架，跳过

            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image_url.url,
                'price': sku.price
            })

        # 3、构建响应数据
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'skus': skus
        })


    def post(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')

        # 2、校验参数
        if not sku_id:
            return JsonResponse({'code': 400, 'errmsg': '参数缺失！'})

        # 如果sku_id是字符串，我们还要判断是否是纯数字
        if isinstance(sku_id, str) and not sku_id.isdigit():
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        try:
            # 3、数据处理
            # 3.1 获取history缓存链接
            conn = get_redis_connection('history')
            pl = conn.pipeline()
            # 3.2 写入历史记录
            # lrem history_1 0 14
            pl.lrem('history_%s'%request.user.id, 0, sku_id)
            # lpush history_1 14
            pl.lpush('history_%s'%request.user.id, sku_id)
            # ltrim history_1 0 4
            pl.ltrim('history_%s'%request.user.id, 0, 4)
            pl.execute()
        except Exception as e:
            logger.info(e)
            return JsonResponse({'code': 400, 'errmsg': 'redis存入失败！'})


        # 写入数据库
        sku = SKU.objects.get(pk=sku_id)
        try:
            v_instance = GoodsVisitCount.objects.get(
                category_id=sku.category_id,
                date=timezone.localtime().date()
            )
        except GoodsVisitCount.DoesNotExist as e:
            GoodsVisitCount.objects.create(
                category_id=sku.category_id,
                count=1,
                date=timezone.localtime().date()
            )
        else:
            v_instance.count += 1
            v_instance.save()


        # 4、构建响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})




class UsernameCountView(View):

    def get(self, request, username):

        try:
            # 1、根据username统计用户数量
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error('数据库访问失败！')
            return JsonResponse({
                'code': 400,
                'errmsg': '数据库访问错误！'
            })


        # 2、构建响应结果返回
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })


class MobileCountView(View):

    def get(self, request, mobile):

        # 1、根据mobile查询用户数量
        count = User.objects.filter(mobile=mobile).count()
        # 2、构建响应结果返回
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })



import json,re
from django_redis import get_redis_connection
from django.contrib.auth import login
class RegisterView(View):

    def post(self, request):

        # 1、数据校验
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        allow = data.get('allow')

        # 1.1 必传字段校验
        if not all([username, password, password2, mobile, sms_code]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数有误！'
            })

        # 1.2 用户名校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': "用户名有误！"
            })

        # 1.3 密码校验
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误！'
            })
        if password != password2:
            return JsonResponse({
                'code': 400,
                'errmsg': '两次输入密码不匹配！'
            })

        # 1.4 手机号验证
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'code': 400,
                'errmsg': '手机格式有误！'
            })

        # 1.5 短信验证码校验
        if not re.match(r'\d{6}', sms_code):
            return JsonResponse({
                'code': 400,
                'errmsg': '手机验证码有误！'
            })

        # 1.6 allow字段校验
        if not isinstance(allow, bool):
            return JsonResponse({
                'code': 400,
                'errmsg': 'allow字段有误！'
            })

        # 1.7 确定用户是否勾选协议
        if allow != True:
            return JsonResponse({
                'code': 400,
                'errmsg': '请同意用户协议！'
            })

        # 1.8 短信验证码比对
        conn = get_redis_connection('verify_code')
        sms_code_from_redis = conn.get('sms_%s'%mobile)
        if not sms_code_from_redis:
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码过期！'
            })

        if sms_code != sms_code_from_redis.decode():
            return JsonResponse({
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
            return JsonResponse({
                'code': 400,
                'errmsg': '写入数据库失败！'
            })


        # 4、使用session记录用户登陆信息
        # request.session['username'] = user.username
        login(request, user) # login帮助我们把用户数据写入session缓存中

        # 5、构建响应
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        response.set_cookie('username', user.username, max_age=3600*24*14)
        return response


from django.contrib.auth import authenticate
class LoginView(View):

    def post(self, request):
        # 1、数据校验
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 1.1 必传校验
        if not all([username, password]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数有误！'
            })

        # 1.2 用户名校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': "用户名有误！"
            })

        # 1.3 密码校验
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return JsonResponse({
                'code': 400,
                'errmsg': '密码格式有误！'
            })
        
        # 1.4 校验remembered字段
        if not isinstance(remembered, bool):
            return JsonResponse({
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
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码有误！'})

        # 3、判断是否需要记住用户登陆状态,用户数据写入session(redis缓存)
        login(request, user)
        if remembered:
            request.session.set_expiry(None) # 默认保存2周
        else:
            request.session.set_expiry(0) # 浏览器关闭清楚session,删除redis中记录的用户缓存数据

        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })

        response.set_cookie('username', user.username, max_age=3600*24*14)

        return merge_cart_cookie_to_redis(request, user, response)




from django.contrib.auth import logout
class LogoutView(View):

    def delete(self, request):
        # 1、清除用户登陆session数据
        # 首先根据request.COOKIES中的sessionid,在根据sessionid查找到缓存中的用户数据，然后删除
        logout(request)
        # 2、删除cookie数据
        response = JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })
        response.delete_cookie('username')
        return response



from meiduo_mall.utils.view import login_required,LoginRequiredMixin
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
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': request.user.username,
                'mobile': request.user.mobile,
                'email': request.user.email,
                'email_active': request.user.email_active

            }
        })



class EmailView(LoginRequiredMixin, View):

    def put(self, request):
        # 1、提取参数
        # b'{"email": '1@2.com'}'
        data_bytes = request.body
        # '{"email": '1@2.com'}'
        data_str = data_bytes.decode()
        # {"email": '1@2.com'}
        data = json.loads(data_str)

        email = data.get('email')

        # 2、校验参数
        if not email:
            return JsonResponse({'code': 400, 'errmsg': '缺失参数！'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '邮箱格式有误！'})


        # 3、更新用户email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code':400, 'errmsg': '数据库错误！'})

        # 4、发送验证邮件：邮件内容中包含一个链接，用户点击该链接完整验证
        # 针对不同的用户，生产不同的token。{"user_id": 1, "email": "1@2.com"}
        token = request.user.generate_token()
        verify_url = settings.EMAIL_VERIFY_URL + token

        # 发布任务函数
        send_verify_email.delay(email, verify_url)

        # 5、构建响应
        return JsonResponse({'code':0, 'errmsg':'ok'})



class VerifyEmailView(View):

    def put(self, request):

        # 1、提取验证请求中的查询字符串参数token
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'code':400, 'errmsg':'token缺失！'})

        # 2、校验token值，获取用户身份
        user = User.check_token(token)
        if user is not None:
            # 2.1 验证成功，修改email_active参数为True
            user.email_active = True
            user.save()
            return JsonResponse({'code':0,'errmsg':'ok'})
        
        return JsonResponse({'code': 400, 'errmsg': '邮箱验证失败！'})



from .models import Address
from meiduo_mall.utils.view import LoginRequiredMixin
class CreateAddressView(LoginRequiredMixin, View):

    def post(self, request):
        # 新增用户地址
        # 1、接受前端传值
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        # 2、校验
        if not all([receiver, province_id, city_id,district_id, place, mobile]):
            return JsonResponse({'code':400, 'errmsg':'缺少必要参数！'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})


        # 3、创建Address模型类对象并保存
        # data = {"receiver": '韦小宝'} --> create(**data) --> create(receiver='韦小宝')
        data['user'] = request.user
        try:
            address = Address.objects.create(**data)

            # 如果该用户没有设置默认地址，那么在新建地址的时候，把该地址设置为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            print(e)
            return JsonResponse({'code':400, 'errmsg': '数据库错误！'})

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
        })




class AddressView(LoginRequiredMixin, View):

    def get(self, request):
        # 1、查询该用户的所有地址
        user_addresses = Address.objects.filter(user=request.user, is_deleted=False)

        addresses = []
        # 2、构造响应数据
        for address in user_addresses:

            # 如果当前address是用户默认地址，追加到列表头部
            if address.id == request.user.default_address_id:
                addresses.insert(0, {
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email
                })
            else:
                # address模型类对象
                addresses.append({
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email
                })


        return JsonResponse({
            'code': 0,
            'errmsg':'ok',
            'default_address_id': request.user.default_address_id,
            'addresses':addresses
        })



class UpdateDestroyAddressView(View):

    def put(self, request, address_id):
        # 1、接受前端传值
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')

        # 2、校验
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必要参数！'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})

        # 3、更新地址
        try:
            # data = {"province": "芜湖市", "province_id": 34}
            # update(province=<对象>),更新或者新建模型类对象的外键字段必须赋值成关联对象
            # 而前端传来的是字符串；另外，我们是根据关联的主键id新建/更新的；
            data.pop('province')
            data.pop('city')
            data.pop('district')
            Address.objects.filter(
                pk=address_id
            ).update(**data)
        except Exception as e:
            print(e)
            return JsonResponse({'code':400, 'errmsg': '更新失败！'})

        address = Address.objects.get(pk=address_id)
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
        })

    def delete(self, request, address_id):

        try:
            # 1、    根据addredd_id获取删除的地址对象
            address = Address.objects.get(pk=address_id)
            # 2、标记逻辑删除（更具局部字段）
            address.is_deleted = True
            address.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '删除失败！'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})






class DefaultAddressView(View):

    def put(self, request, address_id):

        try:
            #  更新默认地址，本质上就是修改当前登陆用户的default_address_id外间关联的主键
            user = request.user
            # 直接赋值外键关联数据的主键id值
            user.default_address_id = address_id
            # user.default_address = Address.objects.get(pk=address_id)
            user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': "数据库错误！"})

        return JsonResponse({'code':0, 'errmsg':'ok'})




class UpdateTitleAddressView(View):


    def put(self, request, address_id):

        # 1、前端传参
        data = json.loads(request.body.decode())
        title = data.get('title')

        if not title:
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数！'})

        if len(title) > 20:
            return JsonResponse({'code': 400, 'errmsg': '地址名称格式不符！'})

        # 2、更新地址的title字段
        try:
            address = Address.objects.get(pk=address_id)
            address.title = title
            address.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '数据库错误！'})

        # 3、构建响应
        return JsonResponse({'code':0, 'errmsg': 'ok'})




class ChangePasswordView(LoginRequiredMixin, View):

    def put(self, request):
        # 1、提取前端参数
        data = json.loads(request.body.decode())
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')

        # 2、校验
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传字段！'})

        if new_password2 != new_password:
            return JsonResponse({'code': 400, 'errmsg': '两次数据不一致！'})

        # 判断旧密码是否正确
        user = request.user
        if not user.check_password(raw_password=old_password): # 传入明文密码
            return JsonResponse({'code': 400, 'errmsg': '密码输入错误！'})

        # 3、修改新密码
        # 注意：不能直接赋值，不会加密
        # user.password = new_password
        user.set_password(raw_password=new_password) # 加密
        user.save()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})














