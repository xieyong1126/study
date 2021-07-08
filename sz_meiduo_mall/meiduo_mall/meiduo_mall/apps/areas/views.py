from django.shortcuts import render
from django.views import View
from meiduo_mall.apps.areas.models import Area
from django import http
from django.core.cache import cache

# Create your views here.

class ProvinceListView(View):

    def get(self, request):
        # 1、获取省模型类对象(查询集)

        # 尝试着从缓存中读数据
        province_list = []

        province_list = cache.get('province_list')

        if not province_list:
            provinces = Area.objects.filter(parent=None)
            province_list = []
            # 2、把模型类对象转化成字典(多个对象就是列表套字典)
            for province in provinces:
                # province：省Area对象
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })

            # 缓存回填
            cache.set('province_list', province_list, 3600)

        return http.JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list
        })



class SubsAreaView(View):

    def get(self, request, pk):
        # pk传过来的是父级行政区主键
        # 1、如果pk是省，过滤出来的就是市
        # 2、如果pk是市，过滤出来的就是区

        sub_data = None
        sub_data = cache.get('sub_area_%s'%pk)

        if not sub_data:
            # 缓存不存在
            f_area = Area.objects.get(pk=pk)
            subs = Area.objects.filter(parent_id=pk)

            sub_data = {
                "id": f_area.id,
                "name": f_area.name,
                "subs": [] # 子级别行政区
            }

            for sub in subs:
                # sub:子级行政区对象
                sub_data['subs'].append({
                    'id': sub.id,
                    'name': sub.name
                })

            cache.set('sub_area_%s'%pk, sub_data, 3600)


        return http.JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sub_data': sub_data
        })

