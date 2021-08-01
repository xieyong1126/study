from rest_framework.viewsets import ModelViewSet
from goods.models import *
from meiduo_admin.serializers.goods_serializers import *
from meiduo_admin.utils.pages import MyPage


class GoodsSpecsViewSET(ModelViewSet):
    queryset = GoodsSpecification.objects.all()
    serializer_class = GoodsSpecsModelSerializer

    pagination_class = MyPage
