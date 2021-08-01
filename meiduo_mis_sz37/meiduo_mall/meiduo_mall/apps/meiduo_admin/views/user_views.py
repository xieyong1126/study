from rest_framework.generics import ListAPIView,CreateAPIView
from users.models import User
from meiduo_admin.serializers.user_serializers import UserModelSerializer
from rest_framework.response import Response


#自定义一个分页器
from rest_framework.pagination import PageNumberPagination
class MyPage(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    page_size = 5
    max_page_size = 10

    def get_paginated_response(self, data):

        return Response({
            'count':self.page.paginator.count,
            'lists':data,
            'page':self.page.number,
            'pages':self.page.paginator.num_pages,
            'pagesize':self.page_size
        })


class UserAPIView(ListAPIView,CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

    pagination_class = MyPage

    #过滤
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:

            return self.queryset.filter(username__contains=keyword,is_staff=True)
        return self.queryset.filter(is_staff=True)


