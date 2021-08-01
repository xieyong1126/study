from django.shortcuts import render
from django.views import View
from users.models import Address
from meiduo_mall.utils.view import LoginRequiredMixin
from goods.models import SKU
from .models import OrderInfo,OrderGoods
from django.http import JsonResponse
from django.utils import timezone
from carts.utils import get_redis_carts
import json
from decimal import Decimal
from django_redis import get_redis_connection
from django.db import transaction
from django.conf import settings
# Create your views here.



class OrderCommitView(LoginRequiredMixin, View):

    # @transaction.atomic # 当前post视图函数中所有的数据库操作即成一个事务
    # 此种装饰2个缺点：1、范围太大；2、无法执行回滚节点
    def post(self, request):

        # 1、提取参数
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        # 1.1 参数校验
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '参数缺失！'})

        if pay_method not in [1,2]:
            return JsonResponse({'code': 400, 'errmsg': '未知支付方式！'})

        if not isinstance(address_id, int):
            return JsonResponse({'code': 400, 'errmsg': '参数有误！'})

        # 2、新建OrderInfo
        # order_id订单主键，自己构造：(1)、不同的用户必须唯一 （2）针对同一个用户也是唯一
        # 针对需求(1)，可以把用户的id拼接；针对需求(2)拼接当前生成订单的时间戳字符串
        # 20200630160756000002
        # timezone.now() # 返回0时区表示的当前时间点对象
        # timezone.localtime() # 返回当前时区表示的当前时间点对象
        local_time = timezone.localtime()
        # 20200630160756 ---->  年月日时分秒 ----> "%Y%m%d%H%M%S"
        # 200630160756 ---->  年月日时分秒 ----> "%y%m%d%H%M%S"
        local_time_str = local_time.strftime("%Y%m%d%H%M%S") # 将时间对象按照指定的格式输出成字符串
        # 20200630160756000002
        order_id = local_time_str + "%06d"%request.user.id

        # 3.1 从用户的购物车中提取sku商品数据
        # redis_cart= {b'14': b'5'}
        # redis_selected = {b'14'}
        redis_cart, redis_selected = get_redis_carts(request)
        with transaction.atomic():

            # 记录一个事务执行的节点
            save_id = transaction.savepoint()

            order = OrderInfo(
                order_id=order_id, # 主键唯一
                user=request.user,
                address_id=address_id,
                total_count=0, # 先初始化为0，后续新增sku订单商品的之后再修改
                total_amount=0,
                freight=Decimal('10.0'),
                pay_method=pay_method
            )
            # 后续新建订单商品从表数据之前，必须先把主表数据创建出来
            order.save()
            # 3、新建OrderGoods
            # 3.2 根据选中的sku商品，添加到OrderGoods
            # 加入乐观锁之后，我们后续的每一次循环的sku都需要读2次，此处就不能先一次性读取所有的skus
            # skus = SKU.objects.filter(id__in=redis_selected)
            # {14: {"count": 5, "selected": True}}
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                # sku_id: b'14'
                # count: b'5'
                if sku_id in redis_selected:   # 只保存被选中的sku商品
                    cart_dict[int(sku_id)] = {
                        "count": int(count),
                        "selected": sku_id in redis_selected
                    }

            # [14....]
            sku_ids = cart_dict.keys()
            for sku_id in sku_ids:
                # sku:模型类对象
                # 每在购物车商品数据中遍历出一个sku，就需要在订单商品中间表中插入一条数据

                while True:
                    # 乐观锁第一次读取
                    sku = SKU.objects.get(pk=sku_id)
                    old_stock = sku.stock
                    old_sales = sku.sales

                    # 下单数量
                    count = cart_dict[sku_id]["count"]

                    # 判断库存
                    if count > old_stock:
                        # 如果库存失败回滚到新建订单之前到节点
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code': 400, 'errmsg': '库存不足！'})

                    # 销量累加，库存要减少
                    # sku.sales += count
                    # sku.stock -= count
                    # sku.save()

                    # =======计算的过程======实际业务中，该计算过程可能非常复杂且漫长，意味着此处可能有别的事务介入
                    new_stock = old_stock - count
                    new_sales = old_sales + count

                    # 在按照旧的库存和销量读取，如果得到则没有别的事务介入，直接修改
                    # 如果按照旧的库存和销量读取，没有读到则数据被别的事务改变，result值为0
                    result = SKU.objects.filter(
                        pk=sku_id, stock=old_stock, sales=old_sales
                    ).update(
                        stock=new_stock, sales=new_sales
                    )
                    if result == 0:
                        continue
                    break # 如果旧的数据未改变，正常修改，则退出whilt True循环


                # 同类spu销量累加
                spu = sku.spu
                spu.sales += count
                spu.save()

                order_goods = OrderGoods(
                    order=order,
                    sku=sku,
                    count=int(count),
                    price=sku.price
                )

                # 订单的总商品数量累加
                order.total_count += count
                order.total_amount += (sku.price * count)

                # 插入订单商品表数据
                order_goods.save()

            # 运费加入总金额
            order.total_amount += order.freight
            order.save()

            # with语句执行结束之后，会自动提交事务，但是不会清楚已经创建的保存节点
            transaction.savepoint_commit(save_id) # 手动清除保存点


        # 下单成功，需要把用户购物车商品去除
        conn = get_redis_connection('carts')
        for sku_id in redis_selected:
            # sku_id: b'14'
            conn.hdel('carts_%s'%request.user.id, sku_id)
            conn.srem('selected_%s'%request.user.id, sku_id)


        # 4、返回
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):

    def get(self, request):
        # 用户进入结算页面，把用户数据返回，用户生产订单
        user = request.user

        # 1、用户可选地址
        address_queryset = Address.objects.filter(
            user=user,
            is_deleted=False
        )
        addresses = []
        for address in address_queryset:
            # address是一个地址模型类对象
            addresses.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'receiver': address.receiver
            })

        # 2、当前用户购物车数据
        # 2.1 从redis购物车中获取选中的sku_id
        # redis_cart = {b'14': b'5'}
        # redis_selected = {b'14'}
        redis_cart, redis_selected = get_redis_carts(request)
        # 2.2 进一步获取sku模型类对象——只取选中的sku
        skus = []
        for sku_id in redis_selected:
            # sku_id: b'14'
            sku = SKU.objects.get(pk=int(sku_id))
            # 2.3 构建skus响应参数
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image_url.url,
                'price': sku.price,
                'count': int(redis_cart[sku_id])
            })

        # 在计算机中，浮点数取的是近似值
        # freight = 3.3 直接保存float类型数据会损失精读
        freight = Decimal('10.0') # Decimal是用来记录十进制数值，是一种数值在python中的精确表达

        # 3、构建响应数据
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'context': {
                "addresses": addresses,
                "skus": skus,
                "freight": freight
            }
        })


















