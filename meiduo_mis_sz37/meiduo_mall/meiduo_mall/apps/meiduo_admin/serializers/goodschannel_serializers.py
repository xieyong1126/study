from goods.models import *
from rest_framework import serializers

class GoodsChannelModelSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()
    group_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    class Meta:
        model = GoodsChannel
        fields = '__all__'



class ChannelGroupModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsChannelGroup
        fields = "__all__"

class GoodsCategoryModelSerializer(serializers.ModelSerializer):
    parent = serializers.StringRelatedField()
    parent_id = serializers.IntegerField()
    class Meta:
        model = GoodsCategory
        fields = "__all__"