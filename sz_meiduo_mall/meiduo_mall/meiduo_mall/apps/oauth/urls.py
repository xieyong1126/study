from django.urls import path,re_path
from . import views

urlpatterns = [
        path('qq/authorization/',views.QQFristView.as_view()),
        path('oauth_callback/',views.QQUserView.as_view()),

]