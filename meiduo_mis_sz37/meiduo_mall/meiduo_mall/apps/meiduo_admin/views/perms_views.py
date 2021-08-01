from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils.pages import MyPage
from django.contrib.auth.models import Permission,ContentType
from meiduo_admin.serializers.perms_serializers import *
from rest_framework.generics import ListAPIView


class PermsModelSetView(ModelViewSet):

    queryset = Permission.objects.all()
    serializer_class = PermsModelSerializer

    pagination_class = MyPage

class PermContentTypeView(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = PermsContenTypeSerializer

