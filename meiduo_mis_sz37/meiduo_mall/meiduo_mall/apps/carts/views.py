from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
import json,base64,pickle

from goods.models import SKU
from django.conf import settings
from carts.utils import *
# Create your views here.


class CartsSimpleView(View):

    def get(self, request):
        # 读取购物车数据，在去读取sku商品对象，构建响应参数
        # {14: {"count": 5, "selected": True}}
        cart_data = {}

        if request.user.is_authenticated:
            # 1、已登陆
            # redis_cart = {b"14": b"3"}
            # redis_selected = {b"14"}
            redis_cart, redis_selected = get_redis_carts(request)

            for sku_id,count in redis_cart.items():
                # sku_id: b'14'
                # count: b'3'
                cart_data[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected
                }

        else:
            # 2、未登陆
            # 所有的商品，不管有没有选中
            cart_data = get_carts_from_cookies(request)


        # 构建响应数据
        cart_skus = []
        sku_ids = cart_data.keys() # [14, 16]
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            # sku：模型类对象
            # 只有当前sku商品是选中状态，才返回
            if cart_data[sku.id]['selected']:
                cart_skus.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': settings.FDFS_URL + sku.default_image_url,
                    'count': cart_data[sku.id]['count']
                })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'cart_skus': cart_skus
        })



class CartSelectAllView(View):

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        selected = data.get('selected')
        # 2、校验
        if not isinstance(selected, bool):
            return JsonResponse({
                'code': 400,
                'errmsg': '数据错误'
            })


        # 3、数据处理
        if request.user.is_authenticated:
            conn = get_redis_connection('carts')
            # redis_cart = {b'14': b'5'}
            # redis_selected = [b'14']
            redis_cart, redis_selected = get_redis_carts(request)
            # sku_ids = [b'14']
            sku_ids = redis_cart.keys()
            if selected:
                # 全选: 把当前所有sku_id加入到集合中
                conn.sadd('selected_%s'%request.user.id, *sku_ids)
            else:
                # 全不选：把当前所有的sku_id从集合中去除
                conn.srem('selected_%s'%request.user.id, *sku_ids)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        else:
            # 未登陆：把cookie购物车所有的sku商品的选中状态设置为当前selected
            cookie_cart = get_carts_from_cookies(request)
            sku_ids = cookie_cart.keys() # [14, 16, 17]
            for sku_id in sku_ids:
                cookie_cart[sku_id]['selected'] = selected

            data = get_cookie_cart_data(cookie_cart)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie(
                'carts',
                data
            )
            return response



class CartsView(View):

    def delete(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')

        if request.user.is_authenticated:
            # 2、已经登陆，删除redis购物车数据
            conn = get_redis_connection('carts')
            conn.hdel('carts_%s'%request.user.id, sku_id)
            conn.srem('selected_%s'%request.user.id, sku_id)
            return JsonResponse({
                'code': 0,
                'errmsg': 'ok'
            })
        else:
            # 3、未登陆，删除cookie中购物车数据并且覆写cookie
            # {14: {"count"5, "selected": True}...}
            cookie_cart = get_carts_from_cookies(request)
            del cookie_cart[sku_id]
            # "HJbgrenjgiernjkb=rgeg"
            data = get_cookie_cart_data(cookie_cart)
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok'
            })
            response.set_cookie(
                'carts',
                data
            )
            return response

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)

        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数！'})

        if isinstance(sku_id, str) and not sku_id.isdigit():
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        if isinstance(count, str) and not count.isdigit():
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        if not isinstance(selected, bool):
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})


        # 3、数据处理
        if request.user.is_authenticated:
            # 3.1 用户已登陆
            # sku_id, count, selected
            # 修改redis购物车中sku_id对应的count值
            conn = get_redis_connection('carts')
            conn.hset('carts_%s'%request.user.id, sku_id, count)
            if selected:
                # 把sku_id加入redis的集合中表示选中
                conn.sadd('selected_%s'%request.user.id, sku_id)
            else:
                # 把sku_id从redis集合中去除，表示取消选中
                conn.srem('selected_%s'%request.user.id, sku_id)

            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'id': sku_id,
                    'count': count,
                    'selected': selected
                }
            })

        else:
            # 3.2 用户未登陆
            # {14: {"count": 5, "selected": True}}
            cookie_cart = get_carts_from_cookies(request)

            # {14: {"count": 3, "selected": False}}
            cookie_cart[sku_id]['count'] = count
            cookie_cart[sku_id]['selected'] = selected

            # "ZBHUJgewgrHJUfgrnewjgkrl"
            data = get_cookie_cart_data(cookie_cart)
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'id': sku_id,
                    'count': count,
                    'selected': selected
                }
            })

            response.set_cookie(
                'carts',
                data
            )
            return response


        # 4、构建响应



    def get(self, request):
        # 购物车数据展示
        # 该字典用来保存读取到的购物车数据
        # {14: {"count": 5, "selected": True}}
        cart_dict = {}

        if request.user.is_authenticated:
            # 1、用户已经登陆，从redis中读取购物车数据
            # redis_cart = {b"14": b"5"}
            # redis_selected = {b"14"}
            redis_cart, redis_selected = get_redis_carts(request)
            for sku_id, count in redis_cart.items():
                # sku_id: b"14"
                # count: b"5"
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_selected
                }

        else:
            # 2、用户未登陆，从cookies中读取购物车数据
            cart_dict = get_carts_from_cookies(request)


        # 3、构建购物车商品数据返回
        sku_ids = cart_dict.keys() # [14]
        carts_skus = []
        for sku_id in sku_ids:
            # sku_id商品的主键
            sku = SKU.objects.get(pk=sku_id)
            carts_skus.append({
                'id': sku.id,
                'name': sku.name,
                'selected': cart_dict[sku_id]['selected'],
                'default_image_url': sku.default_image_url.url,
                'price': sku.price,
                'count': cart_dict[sku_id]['count'],
                # 'amount': sku.price * cart_dict[sku_id]['count']
            })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'cart_skus': carts_skus
        })



    def post(self, request):

        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)

        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数！'})

        if isinstance(sku_id, str) and not sku_id.isdigit():
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        if isinstance(count, str) and not count.isdigit():
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        if not isinstance(selected, bool):
            return JsonResponse({'code': 400, 'errmsg': '参数错误！'})

        # 3、数据处理
        if request.user.is_authenticated: # 3.1 用户已登陆
            # （1）、提取redis中购物车数据
            # carts_<user_id>记录用户商品数据和数量；selected_<user_id>记录被选中的商品
            # redis_cart返回一个字典{b"14": b'5'};
            # redis_selected返回一个集合{b'14'}
            # redis_cart, redis_selected = get_redis_carts(request)

            # （2）、新增当前商品
            # 新增商品在不再我们的缓存中，如果在我们就将它的count累加；如果不再就新增
            # 由于redis提供的hincrby函数可以对现有的sku_id累增，也可以新建，所以无需判断是否存在
            conn = get_redis_connection('carts')
            conn.hincrby('carts_%s'%request.user.id, sku_id, count)
            if selected:
                # 我们需要把当前sku_id加入到选中列表中，自动去重
                conn.sadd('selected_%s'%request.user.id, sku_id)
            else:
                # 如果没有选中，则在选中集合中删除当前sku_id
                conn.srem('selected_%s'%request.user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        else: # 3.2 用户未登陆
            # （1）、尝试着获取用户cookie中的购物车数据 —— 覆盖重写
            # 1、参数传入请求对象
            # 2、返回值就是购物车"字典"数据，如果没有就返回{}
            # {1: {'count': 3, 'selected': True}}
            cookie_cart = get_carts_from_cookies(request)
            # （2）、把用户新添加的购物车商品添加进cookie中
            # 如果原来的cookie购物车有sku商品，那么count就得累加
            if sku_id in cookie_cart:
                # count: 5
                cookie_cart[sku_id]['count'] += count
                cookie_cart[sku_id]['selected'] = selected
            else:
                # 如果原来的cookie购物车没有当前sku商品
                cookie_cart[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            # cookie_cart就是新增购物车数据
            # 重新写入cookie中
            # "BkjkoBHJrfgnjklbnjklb="
            data = get_cookie_cart_data(cookie_cart)

            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie(
                'carts',
                data
            )

            return response














