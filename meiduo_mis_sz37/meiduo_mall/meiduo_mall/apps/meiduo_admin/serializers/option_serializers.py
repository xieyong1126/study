from rest_framework import serializers
from goods.models import SpecificationOption,GoodsSpecification

class OptionModelSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'



class GoodsSpeModelSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()

    class Meta:

        model = GoodsSpecification
        fields = '__all__'