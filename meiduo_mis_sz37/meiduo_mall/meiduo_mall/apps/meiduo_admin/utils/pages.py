# 自定义一个分页器
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
class MyPage(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = 'pagesize'
    page_size = 5 # 后端默认使用的每页数量
    max_page_size = 10 # 最大的每页数据


    # 构造数据返回
    def get_paginated_response(self, data):
        # 参数data：当前页数据序列化的结果
        # 构造符合我们接口定义的分页返回的格式
        return Response({
            'counts': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages':self.page.paginator.num_pages,
            'pagesize': self.page_size
        })