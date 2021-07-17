from django.shortcuts import render
from django.views import View
import json
from django import http
from django_redis import get_redis_connection
import base64, pickle

from apps.goods.models import SKU
# Create your views here.


class CartsView(View):
    """购物车管理：增删改查
    增：POST /carts/
    查：GET /carts/
    改：PUT /carts/
    删：DELETE /carts/
    """

    def delete(self, request):
        """实现删除购物车的逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': 400, 'errmsg': '参数sku_id错误'})

        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果用户已登录，删除redis购物车
            user_id = request.user.id
            # 创建连接到redis的对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除hash中的购物车数据
            pl.hdel('carts_%s'%user_id, sku_id)
            # 删除set中的勾选状态
            pl.srem('selected_%s'%user_id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': 0, 'errmsg': 'OK'})
        else:
            # 如果用户未登录，删除cookie购物车
            # 从cookie中读取购物车字典
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 删除购物车字典中的key
            # 注意点：在删除字典的key时，必须判断字典的key是否存在，只能删除存在的key,如果删了不存在的key,会报错
            if sku_id in cart_dict:
                del cart_dict[sku_id]

            # 将购物车字典转字符串并写入到cookie
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = http.JsonResponse({'code': 0, 'errmsg': 'OK'})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def put(self, request):
        """实现修改购物车的逻辑
        修改购物车和新增购物车百分之九十九是相同的
        """
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        # 如果前端没有传递selected参数，我们给个默认值True,默认被勾选
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': 400, 'errmsg': '参数sku_id错误'})
        try:
            # 使用int类型强转count，如果count不是数字，自动会抛出异常
            count = int(count)
        except Exception:
            return http.JsonResponse({'code': 400, 'errmsg': '参数count错误'})
        # 校验selected类型
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': 400, 'errmsg': '参数selected错误'})

        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果用户已登录，修改redis购物车
            # 由于前端向后端发送的是修改后的数据，所以后端直接覆盖写入即可
            user_id = request.user.id
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset('carts_%s'%user_id, sku_id, count)
            if selected:
                pl.sadd('selected_%s'%user_id, sku_id)
            else:
                pl.srem('selected_%s'%user_id, sku_id)
            pl.execute()

            # 在修改成功后，记得将修改后的数据返回给前端，实现局部刷新的效果
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected
            }

            return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            # 如果用户未登录，修改cookie购物车
            # 由于前端向后端发送的是修改后的数据，所以后端直接覆盖写入即可
            # 从cookie中读取购物车字典
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 修改购物车字典
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将购物车字典转字符串并写入到cookie
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 构造响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected
            }
            response = http.JsonResponse({'code': 0, 'errmsg': 'OK', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def get(self, request):
        """实现查询购物车的逻辑"""
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果用户已登录，查询redis购物车
            user_id = request.user.id
            redis_conn = get_redis_connection('carts')
            # 查询hash中的商品和数量 redis_cart = {b'sku_id1': b'count1', b'sku_id2': b'coun2'}
            redis_cart = redis_conn.hgetall('carts_%s'%user_id)
            # 查询set中的勾选状态 redis_selected = [b'sku_id1']
            redis_selected = redis_conn.smembers('selected_%s'%user_id)

            # 将redis购物车转成可操作的对象：将redis_cart和redis_selected里面的数据合并到一个购物车字典中
            # 使用redis_cart和redis_selected构造一个跟cookie购物车字典一样的字典
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 如果用户未登录，查询cookie购物车
            # 从cookie中读取购物车字典
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        """
        {
            "sku_id1":{
                "count":"1",
                "selected":True
            },
            "sku_id3":{
                "count":"3",
                "selected":False
            }
        }
        """
        # 读取购物车里面的商品信息
        sku_ids = cart_dict.keys()
        sku_model_list = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in sku_model_list:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'count': cart_dict[sku.id]['count'],
                'selected': cart_dict[sku.id]['selected'],
                'amount': sku.price * cart_dict[sku.id]['count']
            })

        # 响应结果
        return http.JsonResponse({'code':0, 'errmsg':'ok', 'cart_skus': cart_skus})

    def post(self, request):
        """实现新增购物车的逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        # 如果前端没有传递selected参数，我们给个默认值True,默认被勾选
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.JsonResponse({'code': 400, 'errmsg': '参数sku_id错误'})
        try:
            # 使用int类型强转count，如果count不是数字，自动会抛出异常
            count = int(count)
        except Exception:
            return http.JsonResponse({'code': 400, 'errmsg': '参数count错误'})
        # 校验selected类型
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': 400, 'errmsg': '参数selected错误'})

        # 实现核心逻辑：登录用户和未登录用户新增购物车
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果用户已登录，新增redis购物车
            # hash：carts_user_id: {sku_id1: count1, sku_id2: count2, ...}
            # set：selected_user_id: [sku_id1]
            # 创建连接到redis5号库的对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            user_id = request.user.id
            # 操作hash，增量存储sku_id和count
            pl.hincrby('carts_%s'%user_id, sku_id, count)
            # 操作set，如果selected为True，需要将sku_id添加到set
            if selected:
                pl.sadd('selected_%s'%user_id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': 0, 'errmsg': 'OK'})
        else:
            # 如果用户未登录，新增cookie购物车
            # 1.从cookie中读取购物车字典
            # 从cookie中读取之前保存的购物车密文字符串
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将密文字符串转成bytes类型的密文字符串
                cart_str_bytes = cart_str.encode()
                # 将bytes类型的密文字符串使用base64解码为bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将bytes类型的字典使用pickle反序列化为python字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 2.添加购物车数据到购物车字典
            if sku_id in cart_dict:
                # 如果要添加的商品在购物车已存在，累加数量
                origin_count = cart_dict[sku_id]['count']
                count += origin_count # count = origin_count + count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 3.购物车字典转字符串并写入到cookie
            # 先使用pickle将cart_dict序列化为bytes类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 在使用base64将bytes类型的字典编码为bytes类型的密文字符串
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 然后再将bytes类型的密文字符串转正真的字符串
            cookie_cart_str = cart_str_bytes.decode()

            # 最后将密文字符串写入到cookie
            response = http.JsonResponse({'code': 0, 'errmsg': 'OK'})
            response.set_cookie('carts', cookie_cart_str)
            return response
