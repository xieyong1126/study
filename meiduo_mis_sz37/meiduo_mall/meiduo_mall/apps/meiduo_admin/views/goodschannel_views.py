
from rest_framework.viewsets import ModelViewSet
from goods.models import *
from meiduo_admin.serializers.goodschannel_serializers import *
from meiduo_admin.utils.pages import MyPage
from rest_framework.generics import ListAPIView



class GoodsChannelModeViewSet(ModelViewSet):

    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelModelSerializer

    pagination_class = MyPage


class ChannelListView(ListAPIView):

    queryset = GoodsChannelGroup.objects.all()
    serializer_class = ChannelGroupModelSerializer

class GoodsCategoryAPIListview(ListAPIView):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategoryModelSerializer

    def get_queryset(self):

        return self.queryset.filter(id__lte=37)