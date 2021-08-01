from rest_framework.viewsets import ModelViewSet
from goods.models import *
from meiduo_admin.serializers.image_serializers import *
from meiduo_admin.utils.pages import MyPage
from rest_framework.generics import ListAPIView

class ImageModelViewSet(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = ImageModelSerializer

    pagination_class = MyPage


class SKUidListAPIView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUModelSerializer