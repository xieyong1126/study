"""
自定义传统身份认证后端，实现可以用手机号验证用户
"""


from django.contrib.auth.backends import ModelBackend
from meiduo_mall.apps.users.models import User

class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写，实现使用用户名或手机号登陆
        :param request: 请求对象
        :param username: 用户名或手机号
        :param password:密码
        :param kwargs:
        :return: 用户对象/None
        """

        # 先按照用户名查找，找不到再按照手机号去查找
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            # 用户名未找到，再尝试着按照手机号去查找
            try:
                user = User.objects.get(mobile=username)
            except User.DoesNotExist as e:
                # 1、两个都找不到 —— 用户不存在
                return None

        # 2、检查密码
        if not user.check_password(password):
            return None

        return user














