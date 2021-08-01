from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings
# Create your models here.



# 由于以下2点，所以我们需要自定义用户模型类，并继承Django点抽象用户基类
# 1、Django默认用户模型类中没哟mobile字段
# 2、Django默认用户模型类中的一些验证方法我们需要使用
class User(AbstractUser):

    # 添加该字段记录用户手机号
    mobile = models.CharField(
        max_length=11, unique=True, verbose_name='手机号'
    )

    # 新增 email_active 字段
    # 用于记录邮箱是否激活, 默认为 False: 未激活
    email_active = models.BooleanField(default=False,
                                       verbose_name='邮箱验证状态')

    # 管联Address对象，代表当前用户的默认地址
    default_address = models.ForeignKey('Address',
                                        related_name='users',
                                        null=True,
                                        blank=True,
                                        on_delete=models.SET_NULL,
                                        verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


    def generate_token(self):

        # 针对不同的用户生产不同的token值
        serializer = TimedJSONWebSignatureSerializer(
            settings.SECRET_KEY,
            60*60*24, # 激活链接中token的有效期
        )

        data = {
            "user_id": self.id,
            "email": self.email
        }

        token = serializer.dumps(data).decode()

        return token

    # @classmethod
    # def check_token(cls, token):
    @staticmethod
    def check_token(token):
        """
        验证token，并且获取用户对像返回
        """
        from itsdangerous import TimedJSONWebSignatureSerializer
        from django.conf import settings

        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)

        try:
            payload = serializer.loads(token)
        except Exception as e:
            print(e)
            return None  # token验证失败

        user_id = payload.get('user_id')
        email = payload.get('email')

        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            print(e)
            return None

        return user

# 设置密码
# User.set_password()
# 验证密码
# User.check_password()
# from django.contrib.auth import authenticate
# authenticate(username=xxx, password=xxxx)传入用户名和密码，传统身份认证
# 密码不会自动加密
# User.objects.create(username=xxx, password=xxx)
# 密码自动加密
# User.objects.create_user(username=xx, password=xx)
# is_authenticated == True  ： 该用户经过身份认证(有身份)
# User.is_authenticated
# from django.contrib.auth.models import AnonymousUser
# AnonymousUser() ---> 匿名用户对象  ---> django默认的身份认证后端验证用户失败，统一返回匿名用户对象
# AnonymousUser().is_authenticated --> False


# 增加地址的模型类, 放到User模型类的下方:
from meiduo_mall.utils.BaseModel import BaseModel
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')

    province = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='province_addresses',
                                 verbose_name='省')

    city = models.ForeignKey('areas.Area',
                             on_delete=models.PROTECT,
                             related_name='city_addresses',
                             verbose_name='市')

    district = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='district_addresses',
                                 verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,
                           null=True,
                           blank=True,
                           default='',
                           verbose_name='固定电话')

    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')

    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_addresses'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']










