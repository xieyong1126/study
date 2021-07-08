from django.urls import re_path,path
from . import views

urlpatterns = [

    re_path(r'^areas/$', views.ProvinceListView.as_view()),
    re_path(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubsAreaView.as_view()),
]