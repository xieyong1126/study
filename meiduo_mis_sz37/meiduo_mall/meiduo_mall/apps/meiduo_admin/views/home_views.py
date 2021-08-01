from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from django.utils import timezone
from orders.models import OrderInfo
from datetime import datetime,timedelta
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.home_serializers import GoodsVisitCountModelSerializer
def get_local_0_time():
    cur_time = timezone.localtime()

    local_0_time = cur_time.replace(hour=0,minute=0,second=0)
    return local_0_time


#用户总量统计
class UserTotalCountView(APIView):

    def get(self,request):
        count = User.objects.count()
        date = timezone.localtime().date()

        return Response({
            'count':count,
            'date':date
        })

#日增用户统计
class UserDayCountView(APIView):

    def get(self,request):
        local_0_time = get_local_0_time()

        count = User.objects.filter(date_joined__gte=local_0_time).count()

        return Response({
            'count':count,
            'date':local_0_time.date()
        })
#日活跃用户统计
class UserActiveCountView(APIView):

    def get(self,request):
        local_0_time = get_local_0_time()

        count = User.objects.filter(last_login__gte=local_0_time).count()

        return Response({
            'count':count,
            'date':local_0_time.date()
        })
#日下单用户量统计
class UserOrderCountView(APIView):
    def get(self,request):
        local_0_time = get_local_0_time()
        orders = OrderInfo.objects.filter(create_time__gte=local_0_time)
        user_set = set()
        for order in orders:
            user_set.add(order.user_id)
        count = len(user_set)

        #方法2
        # users_query = User.objects.filter(orders__create_time__gte=local_0_time)
        # count = len(set(users_query))

        return Response({
            'count':count,
            'date':local_0_time.date()
        })
#月增用户统计
class UserMonthCountView(APIView):
    def get(self,request):
        local_0_time = get_local_0_time()
        start_0_time = local_0_time-timedelta(days=29)

        list = []
        for i in range(30):
            start_time = start_0_time + timedelta(days=i)
            end_time = start_time + timedelta(days=1)
            count = User.objects.filter(date_joined__gte=start_time,date_joined__lte=end_time).count()
            list.append({
                'count':count,
                'date':start_time.date()
            })

        return Response(list)

#日分类商品访问量
# class GoodsDayView(APIView):
#     def get(self,request):
#         local_0_time = get_local_0_time()
#
#         goods = GoodsVisitCount.objects.filter(create_time__gte=local_0_time)
#
#         ser= GoodsVisitCountModelSerializer(instance=goods,many=True)
#
#         return Response(data=ser.data)

from rest_framework.generics import ListAPIView
class GoodsDayView(ListAPIView):
    queryset = GoodsVisitCount.objects.all()
    serializer_class = GoodsVisitCountModelSerializer

    def get_queryset(self):
        local_0_time = get_local_0_time()
        return self.queryset.filter(create_time__gte=local_0_time)