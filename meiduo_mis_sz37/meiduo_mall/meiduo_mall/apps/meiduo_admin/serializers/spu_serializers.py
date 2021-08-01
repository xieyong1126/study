from rest_framework import serializers
from goods.models import *

class SpuModelSerializer(serializers.ModelSerializer):
    # brand = serializers.StringRelatedField()
    # brand_id = serializers.IntegerField()
    # category1_id = serializers.IntegerField()
    # category2_id = serializers.IntegerField()
    # category3_id = serializers.IntegerField()


    class Meta:

        model = SPU
        #fields = '__all__'
        exclude = [
            'category1',
            'category2',
            'category3'
        ]
        #fields = ['category1','category2','category3','name','id']

class BrandModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ['id','name']

class GoodsCategoryModelSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField()
    class Meta:
        model = GoodsCategory
        fields = '__all__'



























