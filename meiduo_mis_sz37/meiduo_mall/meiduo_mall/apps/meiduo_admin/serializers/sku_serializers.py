from rest_framework import serializers
from goods.models import *
from django.db import transaction
from celery_tasks.html.tasks import generate_static_sku_detail_html

class SKUSpecModelSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    class Meta:
        model = SKUSpecification
        fields = ['spec_id','option_id']


class SKUModelSerializer(serializers.ModelSerializer):
    specs = SKUSpecModelSerializer(many=True)
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    class Meta:

        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        validated_data.setdefault('default_image_url', 'group1/M00/00/02/CtM3BVrRdMSAaDUtAAVslh9vkK04466364')
        specs = validated_data.pop('specs')
        sku = None
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 1、新增主表数据：新建sku对象
                sku = super().create(validated_data)
                # 2、插入中间表数据记录规格和选信息
                # sku_id  spec_id  option_id
                for spec in specs:
                # spec = {"spec_id": "6", "option_id": 13}
                    spec['sku_id'] = sku.id
                    SKUSpecification.objects.create(**spec)
            except Exception as e:
                transaction.savepoint_rollback(save_id)

            transaction.savepoint_commit(save_id)
        if not sku:
            raise serializers.ValidationError('创建失败')
        # 事务执行成功，说明新增了一个sku商品,生成静态话页面
        generate_static_sku_detail_html.delay(sku.id)

        return sku


    def update(self, instance, validated_data):
        validated_data.setdefault('default_image_url', 'group1/M00/00/02/CtM3BVrRdMSAaDUtAAVslh9vkK04466364')
        specs = validated_data.pop('specs')

        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 1、新增主表数据：新建sku对象
                sku = super().update(instance,validated_data)
                #删除中间表
                SKUSpecification.objects.filter(sku=sku).delete()
                # 2、插入中间表数据记录规格和选信息
                # sku_id  spec_id  option_id
                for spec in specs:
                    # spec = {"spec_id": "6", "option_id": 13}
                    spec['sku_id'] = sku.id
                    SKUSpecification.objects.create(**spec)
            except Exception as e:
                transaction.savepoint_rollback(save_id)

        transaction.savepoint_commit(save_id)

        # 事务执行成功，说明新增了一个sku商品,生成静态话页面
        generate_static_sku_detail_html.delay(sku.id)

        return instance


class GoodsCategorySimpleSeializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = ['id','name']

class SPUSimpleModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = ['id','name']


class SpecOptModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['id','value']



class SPUSpecModelSerializer(serializers.ModelSerializer):

    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    options = SpecOptModelSerializer(many=True)
    class Meta:
        model = GoodsSpecification
        fields = ['id','name','spu','spu_id','options']