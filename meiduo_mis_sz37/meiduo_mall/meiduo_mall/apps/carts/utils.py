"""
定义一些个工具函数：
1、cookies提取购物车
2、构建cookie购物车数据
3、获取redis购物车数据
4、合并购物车数据 —— 用户一旦登陆，我们把cookie购物车合并到redis中
"""

import base64,pickle
from django_redis import get_redis_connection



# 4
def merge_cart_cookie_to_redis(request, user, response):
    """
    合并购物车数据
    :param request: 为了获取cookie购物车数据
    :param user: 根据用户id拼接到redis名称获取该用户到redis购物车数据
    :param response: 为了使用response删除原有cookie购物车数据
    :return: 返回响应对象
    """

    # 1、提取cookie购物车数据
    # {14: {"count": 5, "selected": True}} or {}
    cookie_cart = get_carts_from_cookies(request)

    # 2、提取redis购物车数据
    request.user = user # 动态语言的魅力
    # redis_cart = {b"14": b"5"}
    # redis_selected = {b"14"}
    redis_cart, redis_selected = get_redis_carts(request)

    # 3、合并: cookie合并到redis
    # 3.1 cookie中所有的商品(不管是否选中)都合并到redis
    # 3.2 合并之后删除cookie购物车
    # 3.3 cookie中存在到商品如果在redis中则覆盖redis
    # 3.4 cookie中不存在的商品则新写入redis

    conn = get_redis_connection('carts')
    pl = conn.pipeline()

    # # {14: {"count": 5, "selected": True}}
    for sku_id,item  in cookie_cart.items():
        # sku_id: 14
        # item: {"count": 5, "selected": True}
        pl.hset('carts_%s'%user.id, sku_id, item['count'])
        if item['selected']:
            pl.sadd('selected_%s'%user.id, sku_id)
        else:
            pl.srem('selected_%s' % user.id, sku_id)

    pl.execute()

    # 4、通过reponse删除cookie购物车
    response.delete_cookie('carts')
    return response






# 1
def get_carts_from_cookies(request):
    """
    获取cookie中的购物车数据
    :param request: 请求对象
    :return: 购物车字典 or {}
    """
    carts_from_cookies = request.COOKIES.get('carts')
    if carts_from_cookies: # "XdnhjgrbewghjrtebABFGNJEKb="
        # 1、先base64解码
        # b'\x56\x78.....'
        cart_dict1 = base64.b64decode(carts_from_cookies.encode())
        # 2、再pickle解码
        cart_dict2 = pickle.loads(cart_dict1)
        return cart_dict2
    else:
        return {}

# 2
def get_cookie_cart_data(cookie_cart):
    """
    使用pickle和base64对购物车字典数据，编码得出存储到cookie中的字符串
    :param cookie_cart: 购物车字典
    :return: 经过pickle和base64编码后的字符串
    """
    # "BNHJBLOhBHYUKNLNJIK="
    return base64.b64encode(
        pickle.dumps(cookie_cart)
    ).decode()


# 3
def get_redis_carts(request):
    user_id = request.user.id
    redis_cart = None
    redis_selected = None

    conn = get_redis_connection('carts')
    # 读取购物车数据
    # redis_cart = {b"14": b"5"} 或者 返回None
    redis_cart = conn.hgetall('carts_%s'%user_id)
    # 读取选中信息
    # redis_selected={b"14"} 后者 返回None
    redis_selected = conn.smembers('selected_%s'%user_id)

    if not redis_cart:
        redis_cart = {} # 如果缓存不存在，则返回空字典
    if not redis_selected:
        redis_selected = set() # 如果缓存不存在则返回空集合

    return redis_cart, redis_selected