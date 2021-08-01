from rest_framework.viewsets import ModelViewSet
from goods.models import *
from meiduo_admin.serializers.sku_serializers import *
from meiduo_admin.utils.pages import MyPage
from rest_framework.generics import ListAPIView

#查询获取sku表列表数据,  保存SKU数据
class SKUViewSet(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUModelSerializer

    pagination_class = MyPage

    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)

        return self.queryset.all()

#获取三级分类信息
class GoodsCateSimpleView(ListAPIView):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategorySimpleSeializer

    def get_queryset(self):

        return self.queryset.filter(parent_id__gte=37)

#获取spu表名称数据
class SPUSimpleView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleModelSerializer

#获取SPU商品规格信息
class SpecSimpleView(ListAPIView):
    queryset = GoodsSpecification.objects.all()
    serializer_class = SPUSpecModelSerializer

    def get_queryset(self):
    # 前端会在路径参数中传一个pk参数
    # 根据这个pk(SPU商品的主键)，过滤出拥有的规格，然后序列化返回这些规格

    # 如何在一个非视图函数中，获取命名分组参数
    # 答：self.kwargs就是用于保存命名分组参数;self.args用于保存非命名分组参数
        pk = self.kwargs.get('pk')

        return self.queryset.filter(spu_id=pk)


#更新SKU表数据