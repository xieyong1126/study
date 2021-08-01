from django.urls import path,re_path
from meiduo_admin.views import LoginView,home_views,user_views,sku_views
from meiduo_admin.views.sku_views import *
from rest_framework_jwt.views import obtain_jwt_token
from meiduo_admin.views.goods_views import *
from meiduo_admin.views.option_views import *
from meiduo_admin.views.spu_views import *
from meiduo_admin.views.goodschannel_views import *
from meiduo_admin.views.goodschannel_views import *
from meiduo_admin.views.brands_views import *
from meiduo_admin.views.image_views import *
from meiduo_admin.views.orders_views import *
from meiduo_admin.views.perms_views import *
from meiduo_admin.views.group_views import *
from meiduo_admin.views.admin_views import *

urlpatterns = [

    #path('authorizations/',LoginView.LoginAPIView.as_view()),
    path('authorizations/', obtain_jwt_token),

    path('statistical/total_count/',home_views.UserTotalCountView.as_view()),

    path('statistical/day_increment/',home_views.UserDayCountView.as_view()),

    path('statistical/day_active/',home_views.UserActiveCountView.as_view()),

    path('statistical/day_orders/',home_views.UserOrderCountView.as_view()),

    path('statistical/month_increment/',home_views.UserMonthCountView.as_view()),

    path('statistical/goods_day_views/',home_views.GoodsDayView.as_view()),

    path('users/', user_views.UserAPIView.as_view()),

    # sku表管理
    re_path(r'^skus/$', SKUViewSet.as_view({
        'get':'list',
        'post':'create'
    })),
    # 新增sku可选三级分类
    re_path(r'^skus/categories/$', GoodsCateSimpleView.as_view()),
    # 新增sku可选spu数据
    re_path(r'^goods/simple/$', SPUSimpleView.as_view()),

# 信则sku可选规格和选项信息
    re_path(r'^goods/(?P<pk>\d+)/specs/$', SpecSimpleView.as_view()),

    re_path(r'^skus/(?P<pk>\d+)/$',SKUViewSet.as_view({
        'get':"retrieve",
        'put':'update',
        'delete':'destroy'
    })),


    re_path(r'^goods/specs/$',GoodsSpecsViewSET.as_view({
        'get':'list',
        'post':'create',

    })),
    re_path(r'^goods/specs/(?P<pk>\d+)/$',GoodsSpecsViewSET.as_view({
        'get':'list',
        'put':'update',
        'delete':'destroy'
    })),
    re_path(r'^specs/options/$', OptionViewSet.as_view({
        'get': 'list',
        'post': 'create',

    })),
    re_path(r'^specs/options/(?P<pk>\d+)/$', OptionViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'delete': 'destroy'
    })),
    re_path(r'^goods/specs/simple/$',optionsimpleViewSET.as_view({
        'get':'list'
    })),


    re_path(r'^goods/$',SPUModelViewSet.as_view({
        'get':'list',
        'post':'create'
    })),
    re_path(r'^goods/(?P<pk>\d+)/$',SPUModelViewSet.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),

    re_path(r'^goods/brands/simple/$',BrandListAPIView.as_view()),

    re_path(r'^goods/channel/categories/$',GoodsCatoryModelViewSet.as_view({
        'get':'list'
    })),
    re_path(r'^goods/channel/categories/(?P<pk>\d+)/$',GoodsCatoryModelViewSet.as_view({
        'get':'list'
    })),

    re_path(r'^goods/channels/$',GoodsChannelModeViewSet.as_view({
        'get':'list',
        'post':'create'
    })),
    re_path(r'^goods/channels/(?P<pk>\d+)/$',GoodsChannelModeViewSet.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),

    re_path(r'^goods/channel_types/$',ChannelListView.as_view()),
    re_path(r'^goods/categories/$',GoodsCategoryAPIListview.as_view()),

    re_path(r'^goods/brands/$',BrandModelViewSet.as_view({
        'get':'list',
        'post':'create'
    })),
    re_path(r'^goods/brands/(?P<pk>\d+)/$',BrandModelViewSet.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),

    re_path(r'^skus/images/$', ImageModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    re_path(r'^skus/images/(?P<pk>\d+)/$', ImageModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

    re_path(r'^skus/simple/$',SKUidListAPIView.as_view()),

    re_path(r'^orders/$',OrdersModelViewSet.as_view({
        'get':'list',

    })),

    re_path(r'^orders/(?P<pk>\d+)/$', OrdersModelViewSet.as_view({
        'get': 'retrieve'
    })),
    re_path(r'^orders/(?P<pk>\d+)/status/$', OrdersModelViewSet.as_view({
        'patch': 'partial_update'
    })),

    re_path(r'^permission/perms/$',PermsModelSetView.as_view({
        'get':'list',
        'post':'create'
    })),
    re_path(r'^permission/perms/(?P<pk>\d+)/$',PermsModelSetView.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy'
    })),
    re_path(r'^permission/content_types/$', PermContentTypeView.as_view()),

    re_path(r'^permission/groups/$', GroupModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    re_path(r'^permission/groups/(?P<pk>\d+)/$', GroupModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    re_path(r'^permission/simple/$',GroupSimpleView.as_view()),

    re_path(r'^permission/admins/$', AdminModelViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    re_path(r'^permission/admins/(?P<pk>\d+)/$', AdminModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

    re_path(r'^permission/groups/simple/$',GroupListAPIView.as_view()),

]
