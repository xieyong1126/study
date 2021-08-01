from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from goods.models import *
from meiduo_admin.serializers.spu_serializers import *
from meiduo_admin.utils.pages import MyPage

class SPUModelViewSet(ModelViewSet):

    queryset = SPU.objects.all()
    serializer_class = SpuModelSerializer

    pagination_class = MyPage

class BrandListAPIView(ListAPIView):

    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer

class GoodsCatoryModelViewSet(ModelViewSet):

    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategoryModelSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return self.queryset.filter(parent_id=pk)

        return self.queryset.filter(id__lte=37)


