from django.contrib.auth.models import Permission,ContentType
from rest_framework import serializers


class PermsModelSerializer(serializers.ModelSerializer):
    #content_type = serializers.StringRelatedField()

    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'content_type',

        ]


class PermsContenTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = [
            'id','name'
        ]