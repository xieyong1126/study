from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer,BadData
from django.conf import settings

# Create your models here.

class User(AbstractUser):

    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')
    email_active = models.BooleanField(default=False,verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def generate_verify_email_url(self):

        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=60*60*24)

        data = {'user_id':self.id,'email':self.email}

        token = serializer.dumps(data).decode()

        verify_url = settings.EMAIL_VERIFY_URL + token

        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 60 * 24)

        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data.get('user_id')
            email = data.get('email')
        try:
            user = User.objects.get(id=user_id,email=email)
        except Exception as e:
            return None
        else:
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

# 指定django工程使用的用户模型类,在settings中
# 该配置项用户模型类指定，有django特殊的语法规范： '应用:模型类'
# AUTH_USER_MODEL = 'users.User'