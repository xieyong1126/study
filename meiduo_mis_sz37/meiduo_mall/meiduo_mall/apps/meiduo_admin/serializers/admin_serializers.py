from rest_framework import serializers
from users.models import User


class AdminModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'mobile',

            'password',
            'groups',
            'user_permissions'
        ]
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def create(self, validated_data):
        
        #return User.objects.create_superuser(**validated_data)
        
        #1  把中间表字段去除
        groups = validated_data.pop('groups')
        user_permissions = validated_data.pop('user_permissions')
        #2 新建主表
        user = User.objects.create_superuser(**validated_data)
        #3 通过ManyToMany字段的set方法设置中间表数据
        user.groups.set(groups)
        user.user_permissions.set(user_permissions)

        return user