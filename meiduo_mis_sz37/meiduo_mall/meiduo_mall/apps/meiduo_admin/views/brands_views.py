from rest_framework.viewsets import ModelViewSet
from goods.models import *
from meiduo_admin.serializers.brands_serializers import *
from meiduo_admin.utils.pages import MyPage

class BrandModelViewSet(ModelViewSet):

    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer

    pagination_class = MyPage
