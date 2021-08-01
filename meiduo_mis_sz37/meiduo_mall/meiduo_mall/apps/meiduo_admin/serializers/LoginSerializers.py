from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_jwt.utils import jwt_payload_handler,jwt_encode_handler

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(min_length=6,max_length=20,required=True,write_only=True)
#     password = serializers.CharField(min_length=6,max_length=20,required=True,write_only=True)
#
#     def validate(self, attrs):
#         # username = attrs.get('username')
#         # password = attrs.get('password')
#         # user = authenticate(username=username,password=password)
#         user = authenticate(**attrs)
#
#         if not user:
#             raise serializers.ValidationError('用户名或密码错误')
#
#         # 2、生成token值
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#
#         #返回有效数据
#         return {'user':user,'token':token}

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=6,max_length=20,required=True,write_only=True)
    password = serializers.CharField(min_length=6,max_length=20,required=True,write_only=True)

    def validate(self, attrs):
        user = authenticate(**attrs)
        if not user:
            return serializers.ValidationError('用户名或密码错误')
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return {'user':user,'token':token}