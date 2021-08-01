from rest_framework.viewsets import ModelViewSet
from users.models import User
from meiduo_admin.serializers.admin_serializers import *
from meiduo_admin.utils.pages import MyPage
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import Group
from meiduo_admin.serializers.group_serializers import *


class AdminModelViewSet(ModelViewSet):

    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminModelSerializer

    pagination_class = MyPage



class GroupListAPIView(ListAPIView):

    queryset = Group.objects.all()
    serializer_class = GroupModeSerializer




