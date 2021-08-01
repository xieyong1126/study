from rest_framework.viewsets import ModelViewSet
from goods.models import SpecificationOption,GoodsSpecification
from meiduo_admin.serializers.option_serializers import *
from meiduo_admin.utils.pages import MyPage

class OptionViewSet(ModelViewSet):

    queryset = SpecificationOption.objects.all()
    serializer_class = OptionModelSerializer

    pagination_class = MyPage


class optionsimpleViewSET(ModelViewSet):
    queryset = GoodsSpecification.objects.all()
    serializer_class = GoodsSpeModelSerializer



