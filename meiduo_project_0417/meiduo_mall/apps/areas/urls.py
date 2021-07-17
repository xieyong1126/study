from django.urls import path

from . import views


urlpatterns = [
    # 查询省份数据: GET /areas/
    path('areas/', views.ProvinceAreasView.as_view()),

    # 查询城市或者区县数据: GET /areas/(?P<pk>[1-9]\d+)/
    path('areas/<int:parentid>/', views.SubAreasView.as_view()),
]