from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from decimal import Decimal
import json
from django.utils import timezone
from django.db import transaction

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from apps.goods.models import SKU
from apps.users.models import Address
from apps.orders.models import OrderInfo, OrderGoods
# Create your views here.


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交
    POST /orders/commit/
    """

    def post(self, request):
        """保存订单基本信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.JsonResponse({'code': 400, 'errmsg': '参数address_id错误'})
        # 提示：由于支付方式有固定的取值范围[1, 2]，所以对于pay_method的校验，我们需要判断他是否在范围内
        # if pay_method not in [1, 2]:
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.JsonResponse({'code': 400, 'errmsg': '参数pay_method错误'})

        # 在操作订单相关的数据表时，显式的使用事务上下文，开启一次事务
        with transaction.atomic():
            # 在操作数据之前，创建事务保存点，用来记录数据操作前的初始状态，方便回滚还原数据和提交事务的
            save_id = transaction.savepoint()

            try:
                # 生成订单号order_id = '年月日时分秒'+'9位的用户ID' （20200612011749000000001）
                # strftime('时间格式') : 时间对象转时间字符串。时间格式---> %Y%m%d%H%M%S
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d'%request.user.id)
                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id = order_id,
                    user = request.user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0.00),
                    freight = Decimal(10.00),
                    pay_method = pay_method,
                    # 订单的状态是跟支付方式绑定的：如果支付方式==<支付宝>，那么订单的状态是<待支付>，如果支付方式==<货到付款>，那么订单的状态是<待发货>
                    # status = 1 if pay_method==2 else 2
                    status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method==OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从redis读取购物车中被勾选的商品信息
                user_id = request.user.id
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s'%user_id)
                redis_selected = redis_conn.smembers('selected_%s'%user_id)
                new_cart = {} # new_cart = {sku_id1: count1}
                for sku_id in redis_selected:
                    new_cart[int(sku_id)] = int(redis_cart[sku_id])

                # 遍历购物车中被勾选的商品信息
                sku_ids = new_cart.keys()
                # 重要提示：
                    # 在提交订单时，我们查询商品sku绝对不能使用 filter(id__in=sku_ids)
                    # 因为filter返回的是查询集，而查询集有缓存，但是，在提交订单时，我们都是实时获取和更新库存和销量的，此时库存和销量不能是缓存数据
                for sku_id in sku_ids:
                    # 每个商品都是在一个死循环中下单的，有资源竞争就继续，直到库存不足为止
                    while True:
                        # 查询SKU信息
                        sku = SKU.objects.get(id=sku_id)

                        # 获取原始的库存和销量: 作为乐观锁的标记，标记数据操作前的初始状态
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断SKU库存：判断库存是否满足购买量
                        sku_count = new_cart[sku_id]
                        if sku_count > origin_stock: # 如果购买量大于库存，返回"库存不足"
                            # 回滚事务，还原数据
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': 400, 'errmsg': '库存不足'})

                        # 为了放大并发下单时，错误的效果，我会模拟较长的网络延迟
                        # import time
                        # time.sleep(15)

                        # SKU减少库存，增加销量
                        # sku.stock -= sku_count # sku.stock = sku.stock - sku_count
                        # sku.sales += sku_count # sku.sales = sku.sales + sku_count
                        # sku.save()

                        # 计算新的库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        # 使用乐观锁操作SKU减少库存，增加销量
                        # update()的返回值，是影响的行数。如果冲突检测发现资源竞争，那么就不执行update，返回0。反之，就执行update，返回影响的函数
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            # 说明检测到冲突，有资源竞争，重新下单，直到库存不足为止
                            # 每个商品都是在一个死循环中下单的，有资源竞争就继续，直到库存不足为止
                            continue

                        # 修改SPU销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息 OrderGoods（多）
                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price
                        )

                        # 保存商品订单中总价和总数量
                        order.total_count += sku_count # 计算总数量
                        order.total_amount += sku_count * sku.price # 计算总金额

                        # 如果该商品购买成功，我们就跳出死循环
                        break

                # 添加邮费和保存订单信息：邮费只是累加一次，所以不能在循环中累加邮费
                order.total_amount += order.freight # 计算实付款，实付款需要加一次邮费
                order.save()
            except Exception:
                # 使用暴力回滚：使用一个try所有的代码，如果发现任何异常，直接回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': 400, 'errmsg': '下单失败'})

            # 如果订单相关的数据表都操作成功，显式的提交一次事务，同步操作的数据到数据库
            transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品
        # 响应提交订单结果
        return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'order_id': order_id})


class OrderSettlementView(LoginRequiredJSONMixin, View):
    """结算订单
    GET /orders/settlement/
    """

    def get(self, request):
        """实现结算订单的逻辑"""
        # 查询当前登录用户未被逻辑删除的地址
        address_model_list = request.user.addresses.filter(is_deleted=False)

        # 查询redis购物车中被勾选的商品信息
        user_id = request.user.id
        redis_conn = get_redis_connection('carts')
        # redis_cart = {b'sku_id1': b'count1', b'sku_id2': b'count2'}
        redis_cart = redis_conn.hgetall('carts_%s'%user_id)
        # redis_selected = [b'sku_id1']
        redis_selected = redis_conn.smembers('selected_%s'%user_id)

        # new_cart = {sku_id1: count1}
        new_cart = {}
        for sku_id in redis_selected:
            new_cart[int(sku_id)] = int(redis_cart[sku_id])

        # 将地址模型列表转字典列表
        addresses = []
        for address in address_model_list:
            addresses.append({
                'id':address.id,
                'province':address.province.name,
                'city':address.city.name,
                'district':address.district.name,
                'place':address.place,
                'receiver':address.receiver,
                'mobile':address.mobile
            })

        # 将购物车商品数据转字典列表
        sku_ids = new_cart.keys()
        sku_model_list = SKU.objects.filter(id__in=sku_ids)
        skus = []
        for sku in sku_model_list:
            skus.append({
                "id": sku.id,
                "name": sku.name,
                "default_image_url": sku.default_image.url,
                "count": new_cart[sku.id],
                "price": sku.price,
            })

        # 指定邮费
        # 注意点：
            # 邮费是金钱，对于钱的精度必须非常高的，所以金钱的定义不能直接使用简单的float
            # python提供了定义金钱的类型 Decimal
        # freight = 10.0
        freight = Decimal(10.0)

        # 构造响应的数据
        context = {
            'addresses': addresses,
            'skus': skus,
            'freight': freight
        }

        # 响应结果
        return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'context': context})
