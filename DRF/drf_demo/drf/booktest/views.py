from django.shortcuts import render

#==============================APIView===========================================
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.status import *
#
# from .models import *
# from .serializers import *
# # Create your views here.
#
#
# class BooksAPIView(APIView):
#     #GET + /books/
#     def get(self,request):
#         #1获取书本数据
#         books = BookInfo.objects.all()
#         # 2、构建序列化器对象
#         bs = BookInfoSerializer(instance=books,many=True)
#         # 3、序列化返回
#         return Response(data=bs.data,status=HTTP_200_OK)
#     # 新建一本书
#     # POST + /books/
#     def post(self,request):
#          data=request.data
#
#          bs = BookInfoSerializer(data=data)
#
#          if not bs.is_valid():
#              return Response(data=bs.errors,status=HTTP_400_BAD_REQUEST)
#          bs.save()
#
#          return Response(data=bs.data,status=HTTP_201_CREATED)
#
# class BookAPIView(APIView):
#     # 返回单一数据
#     # GET + /books/(?P<pk>\d+)/
#     def get(self,request,pk):
#
#         book = BookInfo.objects.get(pk=pk)
#         bs = BookInfoSerializer(instance=book)
#         return Response(data=bs.data,status=HTTP_200_OK)
#
#     def delete(self,request,pk):
#         book = BookInfo.objects.get(pk=pk)
#         book.delete()
#         return Response(data=None,status=HTTP_204_NO_CONTENT)
#
#     def put(self,request,pk):
#         book = BookInfo.objects.get(pk=pk)
#
#         bs = BookInfoSerializer(instance=book,data=request.data)
#         if not bs.is_valid():
#             return Response(data=bs.errors,status=HTTP_400_BAD_REQUEST)
#         bs.save()
#
#         return Response(data=bs.data,status=HTTP_201_CREATED)
#
#     def patch(self,request,pk):
#         book = BookInfo.objects.get(pk=pk)
#
#         bs = BookInfoSerializer(instance=book,data=request.data,partial=True)
#         if not bs.is_valid():
#             return Response(data=bs.errors, status=HTTP_400_BAD_REQUEST)
#         bs.save()
#
#         return Response(data=bs.data, status=HTTP_201_CREATED)

#==========================GenericAPIView====================================================
# from rest_framework.generics import GenericAPIView
# from rest_framework.response import Response
# from rest_framework.status import *
#
# from .serializers import *
# from .models import *
#
#
# class BooksAPIView(GenericAPIView):
#     # queryset类属性，指定当前视图中get_queryset方法默认返回的查询集
#     queryset = BookInfo.objects.all()
#     # serializer_class类属性，指定当前视图中get_serializer和get_serializer_class使用的序列化器类
#     serializer_class = BookInfoSerializer
#     # 返回列表
#     # GET + /books/
#     def get(self,request):
#         books = self.get_queryset()
#         bs = self.get_serializer(instance=books,many=True)
#         return Response(data=bs.data,status=HTTP_200_OK)
#
#
#     def post(self,request):
#
#         bs = self.get_serializer(data=request.data)
#
#         if not bs.is_valid():
#             return Response(data=bs.errors,status=HTTP_400_BAD_REQUEST)
#         bs.save()
#         return Response(data=bs.data,status=HTTP_200_OK)
#
#
#
# class BookAPIView(GenericAPIView):
#     # queryset类属性，指定当前视图中get_queryset方法默认返回的查询集
#     queryset = BookInfo.objects.all()
#     # serializer_class类属性，指定当前视图中get_serializer和get_serializer_class使用的序列化器类
#     serializer_class = BookInfoSerializer
#
#
#     def get(self,request,pk):
#
#         book = self.get_object()
#         bs = self.get_serializer(instance=book)
#
#         # 该类属性，用来指定get_object函数唯一过滤的依据字段
#         # queryset.get(id=xxx)
#         # lookup_field = "pk" # 默认就是"pk"
#         lookup_field = 'pk'
#         lookup_url_kwarg = lookup_field
#         # 该类属性，用来指定提取过滤字段值的路径分组名称
#         # lookup_url_kwarg = lookup_field  # 默认值等于lookup_field
#
#         return Response(data=bs.data,status=HTTP_200_OK)
#
#     def delete(self,request,pk):
#
#         book = self.get_object()
#         book.delete()
#         return Response(data=None,status=HTTP_204_NO_CONTENT)
#
#     #全更新
#     def put(self,request,pk,**kwargs):
#         partial = kwargs.get('partial',False)
#
#         book = self.get_object()
#         bs = self.get_serializer(instance=book,data=request.data,partial=partial)
#
#         if not bs.is_valid():
#             return Response(data=bs.errors,status=HTTP_400_BAD_REQUEST)
#
#         bs.save()
#
#         return Response(data=bs.data,status=HTTP_201_CREATED)
#
#
#     def patch(self,request,pk):
#         # book = self.get_object()
#         # bs = self.get_serializer(instance=book,data=request.data,partial=True)
#         #
#         # if not bs.is_valid():
#         #     return Response(data=bs.errors,status=HTTP_400_BAD_REQUEST)
#         # bs.save()
#         # return Response(data=bs.data,status=HTTP_201_CREATED)
#
#         return self.put(request,pk,partial=True)

#==================================mixin扩展类============================================================
# from rest_framework.mixins import ListModelMixin,CreateModelMixin,RetrieveModelMixin
# from rest_framework.mixins import UpdateModelMixin,DestroyModelMixin
# from rest_framework.response import Response
# from rest_framework.generics import GenericAPIView
# from rest_framework.status import *
#
# from .models import *
# from .serializers import *
#
# class BooksAPIView(ListModelMixin,CreateModelMixin,GenericAPIView):
#     queryset = BookInfo.objects.all()
#     serializer_class = BookInfoSerializer
#     #查看所有
#     def get(self,requesut):
#
#         return self.list(requesut)
#
#     #新建
#     def post(self,request):
#
#         return self.create(request)
#
# class BookAPIView(RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,GenericAPIView):
#     queryset = BookInfo.objects.all()
#     serializer_class = BookInfoSerializer
#     #单一查看
#     def get(self,request,pk):
#
#         return self.retrieve(request,pk)
#
#     #删除
#     def delete(self,request,pk):
#
#         return self.destroy(request,pk)
#     #全更新
#     def put(self,request,pk):
#
#         return self.update(request,pk)
#
#
#     #部分更新
#     def patch(self,reqeust,pk):
#
#         return self.partial_update(reqeust,pk)

#======================================Mixin + GenericAPIView============================================
# from rest_framework.generics import ListAPIView,CreateAPIView,DestroyAPIView,UpdateAPIView,RetrieveAPIView
#
# from .models import *
# from .serializers import *
#
# class BooksAPIView(ListAPIView,CreateAPIView):
#     queryset = BookInfo.objects.all()
#     serializer_class = BookInfoSerializer
#
#
#
# class BookAPIView(DestroyAPIView,RetrieveAPIView,UpdateAPIView):
#     queryset = BookInfo.objects.all()
#     serializer_class = BookInfoSerializer
#     #单一查看
#
#     #删除
#     #全更新
#
#     #部分更新


#====================================HeroInfo===APIView==================================

# from rest_framework.views import APIView
# from .models import *
# from .serializers import *
# from rest_framework.response import Response
# from rest_framework.status import *
# from rest_framework.generics import GenericAPIView

# class HerosAPIVew(APIView):
#     def get(self,request):
#         heros = HeroInfo.objects.all()
#
#         hs = HeroInfoSerializer(instance=heros,many=True)
#
#         return Response(data=hs.data)
#
#     def post(self,request):
#
#         hs = HeroInfoSerializer(data=request.data)
#
#         hs.is_valid(raise_exception=True)
#
#         hs.save()
#
#         return Response(data=hs.data,status=HTTP_201_CREATED)
#
# class HeroAPIVew(APIView):
#     def get(self,request,pk):
#
#         hero = HeroInfo.objects.get(pk=pk)
#
#         hs = HeroInfoSerializer(instance=hero)
#
#         return Response(data=hs.data)
#
#     def put(self,request,pk):
#
#         hero = HeroInfo.objects.get(pk=pk)
#
#         hs = HeroInfoSerializer(data=request.data,instance=hero)
#
#         hs.is_valid(raise_exception=True)
#
#         hs.save()
#
#         return Response(data=hs.data,status=HTTP_205_RESET_CONTENT)
#     def patch(self,request,pk):
#         hero = HeroInfo.objects.get(pk=pk)
#
#         hs = HeroInfoSerializer(data=request.data, instance=hero,partial=True)
#
#         hs.is_valid(raise_exception=True)
#
#         hs.save()
#         return Response(data=hs.data, status=HTTP_205_RESET_CONTENT)
#
#     def delete(self,request,pk):
#
#         hero = HeroInfo.objects.get(pk=pk)
#
#         hero.delete()
#
#         return Response(data=None,status=HTTP_204_NO_CONTENT)

#=========================================HeroInfo====GENERICAPIView=========================================
# from rest_framework.views import APIView
# from .models import *
# from .serializers import *
# from rest_framework.response import Response
# from rest_framework.status import *
# from rest_framework.generics import GenericAPIView
#
# class HerosAPIVew(GenericAPIView):
#     queryset = HeroInfo.objects.all()
#     serializer_class = HeroInfoSerializer
#
#     def get(self,request):
#
#         heros = self.get_queryset()
#         hs = self.get_serializer(instance=heros,many=True)
#         return Response(data=hs.data)
#
#     def put(self,request):
#         hs = self.get_serializer(data=request.data)
#         hs.is_valid(raise_exception=True)
#         hs.save()
#         return Response(data=hs.data,status=HTTP_201_CREATED)
#
# class HeroAPIVew(GenericAPIView):
#     pass



#==========================================视图集================================
from rest_framework.viewsets import ModelViewSet,ViewSet,GenericViewSet,ReadOnlyModelViewSet
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.decorators import action

# class BooksViewSet(ViewSet):
#
#     # 自定义方法read实现修改阅读量
#     def read(self,request,pk):
#
#         book = BookInfo.objects.get(pk=pk)
#
#         bs = BookInfoSerializer(instance=book,data=request.data,partial=True)
#
#         bs.is_valid(raise_exception=True)
#
#         bs.save()
#
#         return Response(bs.data)

from rest_framework.authentication import SessionAuthentication,BasicAuthentication
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle,ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import filters


# ⾃自定义第⼀一种分⻚页后端
# from rest_framework.pagination import PageNumberPagination
# class MyPageNumpagination(PageNumberPagination):
#     # page_size 每页数目
#     # page_query_param 前端发送的页数关键字名，默认为"page"
#     # page_size_query_param 前端发送的每页数目关键字名，默认为None
#     # max_page_size 前端最多能设置的每页数量
#     page_query_param = 'page'#books/?page=2
#     page_size = 3#自定义每页几个，可以接收前端参数
#     max_page_size = 10#每页最大数量
#     page_size_query_param = 'page_size'# books/?page=2&page_size=5

#自定义第二种分页后端
from rest_framework.pagination import LimitOffsetPagination
class MyLimitOffsetPagination(LimitOffsetPagination):
    limit_query_param = 'limit' #/books/?limit=5 表示取几条数据
    offset_query_param = 'offset'#/books/?offset=3 表示偏移量
    max_limit = 10#每页最大数量
    default_limit = 5#默认取几条

class BooksModelViewSet(ModelViewSet):
    """
    list:
    返回图书详情数据
    retrieve:
    返回图书详情
    latest:
    返回最新的图书数据
    read:
    修改图书的阅读量
    """
 #   queryset = BookInfo.objects.all()
#    serializer_class = BookInfoSerializer


    # ⾃自定义当前视图中使⽤用的身份认证后端
    # authentication_classes = [SessionAuthentication]

    # 局部定义当前视图中使⽤用的权限检查后端
    permission_classes = [AllowAny]

    #具体视图中通过throttle_classess属性来配置,局部指定限流后端
    #throttle_classes = (UserRateThrottle,AnonRateThrottle)

    # 在针对的视图类中局部指定⾃自定义的限流规则
    #throttle_scope = "contacts"
    # 局部指定限流后端
    throttle_classes = [ScopedRateThrottle]

    #在视图中添加filter_fields属性，指定可以过滤的字段
    #filter_backends = [DjangoFilterBackend]
    # 在局部中指定过滤依据的字段
    #filter_fields = ['btitle',]
    #filterset_fields = ['btitle']

    # 局部指定过滤后端
    #filter_backends = [OrderingFilter]
    #指定排序过滤的依据字段
    #ordering_fields = ['bpub_date','bread']

    # 局部设置分⻚页器器
    # pagination_class = MyPageNumpagination
    #pagination_class = MyLimitOffsetPagination

    #如果在视图内关闭分页功能，只需在视图内设置
    #pagination_class = None

    #搜索过滤
    filter_backends = [filters.SearchFilter]
    search_fields = ['btitle']


    # 我们继承子模型类视图集，那么CURD的函数/方法都已经实现了，而且这些方法均符合django视图方法的定义
    # 潜台词：这些方法是可以被用作路由映射的！！

    # 返回列表
    # def list(self, request, *args, **kwargs):
    #     pass

    # 新建单一
    # def create(self, request, *args, **kwargs):
    #     pass

    @action(methods=['patch'], detail=True, url_path='fix_read')
    def read(self, request, pk):
        pass













































