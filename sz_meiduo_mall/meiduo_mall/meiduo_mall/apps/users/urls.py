from django.urls import path,re_path
from . import views

urlpatterns = [
    #/usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UsernameCountView.as_view()),

    #/mobiles/(?P<mobile>1[3-9]\d{9})/count/
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    re_path(r'^register/$', views.RegisterView.as_view()),
    re_path(r'^login/$', views.LoginView.as_view()),
    re_path(r'^logout/$', views.LogoutView.as_view()),
    re_path(r'^info/$', views.UserInfoView.as_view()),
    path('emails/',views.EmailView.as_view()),
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]