from rest_framework.views import APIView
from meiduo_admin.serializers.LoginSerializers import LoginSerializer
from rest_framework.response import Response


# class LoginAPIView(APIView):
#     def post(self,request):
#         #1,构建一个序列化器对象，传入前端参数
#         serializer = LoginSerializer(data=request.data)
#         #2.启动校验流程
#         serializer.is_valid(raise_exception=True)
#
#         #3.校验成功，构建响应
#         return Response({
#             'username':serializer.validated_data['user'].username,
#             'id':serializer.validated_data['user'].id,
#             'token':serializer.validated_data['token']
#         })

class LoginAPIView(APIView):
    def post(self,request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        return Response({
            'username':ser.validated_data['user'].username,
            'user_id':ser.validated_data['user'].id,
            'token':ser.validated_data['token']
        })