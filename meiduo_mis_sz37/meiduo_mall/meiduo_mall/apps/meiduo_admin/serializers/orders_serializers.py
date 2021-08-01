from rest_framework import serializers
from orders.models import *
from goods.models import *


class OrdersModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = ['order_id','create_time']

        extra_kwargs = {
            'create_time':{
                'format':'%Y-%m-%d %H:%M:%S'
            }
        }

class SkuModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = [
            'name',
            'default_image_url'
        ]



class OrderGoodsModelSerializer(serializers.ModelSerializer):
    sku = SkuModelSerializer()#many=True不给加？？？？？
    class Meta:
        model = OrderGoods
        fields = [
            'count',
            'price',
            'sku'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()
    skus = OrderGoodsModelSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
        extra_kwargs = {
            'create_time': {
                'format': '%Y-%m-%d %H:%M:%S'
            }
        }