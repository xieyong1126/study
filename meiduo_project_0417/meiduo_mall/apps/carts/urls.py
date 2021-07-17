from django.urls import path

from . import views


urlpatterns = [
    # 购物车管理：增删改查 /carts/
    path('carts/', views.CartsView.as_view()),
]