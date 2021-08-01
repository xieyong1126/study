from rest_framework import serializers
from goods.models import *
from django.db import transaction

class GoodsSpecsModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()#默认read_only = True
    spu_id = serializers.IntegerField()

    class Meta:
        model = GoodsSpecification
        fields = [
            'id','name','spu','spu_id'
        ]

