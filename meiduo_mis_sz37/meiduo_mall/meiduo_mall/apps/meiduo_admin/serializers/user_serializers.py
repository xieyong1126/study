from rest_framework import serializers
from users.models import User

class UserModelSerializer(serializers.ModelSerializer):


    class Meta:

        model = User
        fields = [
            'id','username','mobile','email','password'
        ]

    extra_kwargs = {
        'password':{'write_only':True}
    }

    def create(self, validated_data):
        # validated_data = {"username":xxx....}
        # 1、密码加密；2、新建用户为is_staff=True
        # create(): 密码不会加密，普通用户
        # create_user(): 密码加密，普通用户
        # create_superuser(): 密码加密，is_staff=True

        return User.objects.create_superuser(**validated_data)