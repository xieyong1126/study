from django.urls import path,re_path
from . import views

# urlpatterns = [
#     # path('books/',views.BooksAPIView.as_view()),
#     # re_path('^books/(?P<pk>\d+)/$',views.BookAPIView.as_view()),
#     # path('heros/',views.HerosAPIVew.as_view()),
#     # re_path(r'^heros/(?P<pk>\d+)/$',views.HeroAPIVew.as_view()),
#
#
# ]


# from django.urls import path,re_path
# from . import views
#
# urlpatterns = [
#
#     #re_path(r'^books/(?P<pk>\d+)/$',views.BooksViewSet.as_view({'patch':'read'})),
#     re_path(r'^books/$',views.BooksModelViewSet.as_view({'get':'list',
#                                                           'put':'create'})),
# ]

#================================自动生成路由================================
from rest_framework.routers import SimpleRouter,DefaultRouter
from . import views



urlpatterns = [

]

#1、构建路路由对象
router = SimpleRouter()
# router = DefaultRouter()
# 2、⾃自动⽣生成映射关系（注册视图集）
# /books/ + GET = self.list
# /books/ + POST = self.create
# /books/(?P<pk>\d+)/ + GET = self.retrieve
# /books/(?P<pk>\d+)/ + PUT = self.update
# /books/(?P<pk>\d+)/ + PATCH = self.partial_update
# /books/(?P<pk>\d+)/ + DELETE = self.destroy
router.register(prefix='books',viewset=views.BooksModelViewSet,basename='booksaaaaaaa')

# 3、添加到路路由映射列列表⾥里里
# router.urls是⼀一个列列表，⾥里里⾯面相当于帮助我们⾃自动写好了了re_path,如下：
# router.urls = [
# re_path(r'^books/$', BooksViewSet.as_view({"get": "list", "post": "create"})),
# re_path(r'^books/(?P<pk>\d+)/$', BooksViewSet.as_view({
# "get": "retrieve",
# "put": "update",
# "patch": "partial_update",
# "delete": "destroy"
# })),
# ]
# urlpatterns.extend(router.urls)
urlpatterns += router.urls