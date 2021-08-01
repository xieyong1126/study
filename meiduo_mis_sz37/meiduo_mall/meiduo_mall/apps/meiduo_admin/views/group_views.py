from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group,Permission
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.perms_serializers import PermsModelSerializer
from meiduo_admin.serializers.group_serializers import *
from meiduo_admin.utils.pages import MyPage


class GroupModelViewSet(ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupModeSerializer

    pagination_class = MyPage


class GroupSimpleView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermsModelSerializer