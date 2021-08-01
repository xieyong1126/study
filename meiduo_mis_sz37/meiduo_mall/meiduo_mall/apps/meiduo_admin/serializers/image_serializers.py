from rest_framework import serializers
from goods.models import *


class ImageModelSerializer(serializers.ModelSerializer):
    # sku = serializers.StringRelatedField()
    # sku_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUImage
        fields = [
            'id',
            'sku',

            # 文件类型字段，序列化的结果
            # 取决于文件存储后端url函数返回的结果！
            'image'
        ]




class SKUModelSerializer(serializers.ModelSerializer):


    class Meta:
        model = SKU
        fields = ['id','name']