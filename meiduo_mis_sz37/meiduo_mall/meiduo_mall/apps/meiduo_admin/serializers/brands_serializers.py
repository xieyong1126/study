from rest_framework import serializers
from goods.models import *

class BrandModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'
