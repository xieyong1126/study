from django.urls import path

from . import views


urlpatterns = [
    # QQ登录扫码链接: GET /qq/authorization/
    path('qq/authorization/', views.QQURLView.as_view()),

    # 处理授权后的回调:GET /oauth_callback/
    path('oauth_callback/', views.QQUserView.as_view()),
]