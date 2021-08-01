from rest_framework.viewsets import ModelViewSet
from orders.models import *
from meiduo_admin.serializers.orders_serializers import *
from meiduo_admin.utils.pages import MyPage

class OrdersModelViewSet(ModelViewSet):

    queryset = OrderInfo.objects.all()
    serializer_class = OrdersModelSerializer

    pagination_class = MyPage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(order_id__contains=keyword)
        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'partial_update':
            return OrderDetailSerializer
        else:
            return self.serializer_class



















