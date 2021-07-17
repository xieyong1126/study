from django.urls import path

from . import views


urlpatterns = [
    # 结算订单: GET /orders/settlement/
    path('orders/settlement/', views.OrderSettlementView.as_view()),
    # 订单提交: POST /orders/commit/
    path('orders/commit/', views.OrderCommitView.as_view()),
]