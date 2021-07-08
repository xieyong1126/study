# from rest_framework import serializers
# from booktest.models import *
#

# class BookInfoSerializer(serializers.Serializer):
#     btitle = serializers.CharField()
#     bpub_date = serializers.DateField()
#     bread = serializers.IntegerField()
#     bcomment = serializers.IntegerField()
#     image = serializers.ImageField()
#     is_delete = serializers.BooleanField()



# class BookInfoSerializer2(serializers.Serializer):
#     btitle = serializers.CharField()
#     bpub_date = serializers.DateField()
#     bread = serializers.IntegerField()

#
# class HeroInfoSerializer(serializers.Serializer):
#     GENDER_CHOICES = (
#         (0, 'male'),
#         (1, 'female')
#     )
#     id = serializers.IntegerField(label='ID', read_only=True)
#     hname = serializers.CharField(label='名字', max_length=20)
#     hgender = serializers.ChoiceField(choices=GENDER_CHOICES, label='性别', required=False)
#     is_delete = serializers.BooleanField(default=False,label='逻辑删除')

    #关联字段
    #1.此字段将被序列化为关联对象的主键。
    #hbook = serializers.PrimaryKeyRelatedField(label='图书',read_only=True)
    #2.此字段将被序列化为关联对象的字符串表示方式（即__str__方法的返回值）
    # hbook = serializers.StringRelatedField(label='图书',read_only=True)
    #3.关联字段自定义序列化
    # hbook = BookInfoSerializer()
    # hbook = BookInfoSerializer2()

# class HeroInfoSerializer2(serializers.Serializer):
#     GENDER_CHOICES = (
#         (0, 'male'),
#         (1, 'female')
#     )
#
#     hname = serializers.CharField(label='名字', max_length=20)
#     hgender = serializers.ChoiceField(choices=GENDER_CHOICES, label='性别', required=False)

#
# def validate_btitle(value):
#     if 'django' not in value.lower():
#         raise serializers.ValidationError('图书不是django相关书籍')
#
#
# class BookInfoSerializer(serializers.Serializer):
#     id = serializers.IntegerField(label='ID',read_only=True)
#     # btitle = serializers.CharField(max_length=20,min_length=2,label='名称',
#     #                                # validators约束条件指定多个针对当前字段的校验函数
#     #                                validators=[validate_btitle])
#     btitle = serializers.CharField(max_length=20, min_length=2, label='名称')
#     bpub_date = serializers.DateField(label='发布日期',required=True)
#     bread = serializers.IntegerField(label='阅读量',required=False,min_value=0)
#     bcomment = serializers.IntegerField(label='评论量',required=False,min_value=0)
#     image = serializers.ImageField(label='图片',required=False,allow_null=True)
#     is_delete = serializers.BooleanField(label='逻辑删除',required=False)

    #validate_<field_name>对<field_name>字段进行验证
    # def validate_bread(self,value):
    #     if value < 10:
    #         raise serializers.ValidationError('阅读量太少')
    #     return value

    #在序列化器中需要同时对多个字段进行比较验证时，可以定义validate方法来验证
    # def validate(self, attrs):
    #     bread = attrs['bread']
    #     bcomment = attrs['bcomment']
    #
    #     if bcomment > bread:
    #         raise serializers.ValidationError('讨论量大于阅读量')
    #     return attrs

    #1.此字段将被序列化为关联对象的主键
    #heroinfo_set = serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    #heros = serializers.PrimaryKeyRelatedField(read_only=True,many=True)
    #2.此字段将被序列化为关联对象的字符串表示方式（即__str__方法的返回值）
    # heros = serializers.StringRelatedField(many=True)
    #3.3）使用关联对象的序列化器
    # heros = HeroInfoSerializer(many=True)
    # heros = HeroInfoSerializer2(many=True)

    #新建
    # def create(self, validated_data):
    #     instance = BookInfo.objects.create(**validated_data)
    #
    #     return instance
    # #更新
    # def update(self, instance, validated_data):
    #     instance.btitle = validated_data.get('btitle', instance.btitle)
    #     instance.bpub_date = validated_data.get('bpub_date', instance.bpub_date)
    #     instance.bread = validated_data.get('bread', instance.bread)
    #     instance.bcomment = validated_data.get('bcomment', instance.bcomment)
    #     instance.is_delete = validated_data.get('is_delete',instance.is_delete)
    #     instance.save()
    #     return instance

#模型类序列化器ModelSerializer
# from rest_framework import serializers
# from .models import BookInfo,HeroInfo

# class BookInfoSerializer(serializers.ModelSerializer):
#     # 非主健字段手动添加
#     #heros = serializers.StringRelatedField(many=True,read_only=True)  ##???
#     class Meta:

        # model:指明参照哪个模型类
        # fields:指明为模型类的哪些字段生成
        #exclude:排除哪些字段
        #可以通过read_only_fields指明只读字段，即仅用于序列化输出的字段
        #使用extra_kwargs参数为ModelSerializer添加或修改原有的选项参数

        #可以添加自定义校验

        # model = BookInfo
        # fields = '__all__'
        #fields = ('id', 'btitle', 'bpub_date')
        # exclude = ['image','id']
        # read_only_fields = ['iamge','id']
        # extra_kwargs = {
        #     'bread':{'min_value':0,'required':True},
        #     'bcomment': {'min_value': 0, 'required': True},
        # }

    #可以添加自定义校验
    # def validate(self, attrs):
    #     btitle = attrs['btitle']
    #     if 'django' not in btitle.lower():
    #         raise serializers.ValidationError('与django无关书箱')
    #     return attrs



#
# class HeroInfoSerializer(serializers.ModelSerializer):
#     # 关联对象的主键隐藏字段不会自动映射
#     # hbook_id = serializers.IntegerField()
#     #hbook = serializers.StringRelatedField()
#
#     class Meta:
#         model = HeroInfo
#         fields = '__all__'

# class HeroInfoSerializer(serializers.ModelSerializer):
#     hbook = serializers.PrimaryKeyRelatedField(queryset=BookInfo.objects.all())
#     class Meta:
#         model = HeroInfo
#         fields= ['id','hname','hbook']




from .models import BookInfo,HeroInfo
from rest_framework import serializers

# class BookInfoSerializer(serializers.Serializer):
#     btitle = serializers.CharField(label='名称',max_length=20)
#     bpub_data = serializers.DateField(label='',allow_null=True)
#     bread = serializers.IntegerField(label='',default=0)
#     is_delete = serializers.BooleanField(label='',default=False)
#
# class HeroInfoSerializer(serializers.Serializer):
#     GENDER_CHOICES = (
#         (0,'male'),
#         (1,'female')
#     )
#
#     id = serializers.IntegerField(label='',read_only=True)
#     hname = serializers.CharField(label='',max_length=20)
#     hgender = serializers.ChoiceField(choices=GENDER_CHOICES,label='')
#     #hbook = serializers.PrimaryKeyRelatedField(read_only=True)
#     hbook = serializers.PrimaryKeyRelatedField(queryset=BookInfo.objects.all())
#     #hbook = serializers.StringRelatedField()
#     #hbook = BookInfoSerializer()

class BookInfoSerializer(serializers.ModelSerializer):


    class Meta:
        model = BookInfo
        fields = '__all__'

class HeroInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = HeroInfo
        fields = '__all__'

