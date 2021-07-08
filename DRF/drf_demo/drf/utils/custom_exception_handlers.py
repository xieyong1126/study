"""
自定义drf异常处理函数
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response

# ObjectDoesNotExist: 模型类查询数据找不不到会抛出的DoesNotExist异常的基类
from django.db.models import ObjectDoesNotExist

def my_exception_handler(exc,context):
    """
    功能：判断异常，构建响应
    :param exc: 捕获到的异常对象
    :param context: 上下文参数
    :return: 响应对象
    """
    #1, 交给drf 自己的异常处理函数处理
    result = exception_handler(exc,context)
    if result is not None:
        #drf自行处理了
        return result

    #2,如果drf自己的异常处理函数无法处理，我们在自行处理
    if isinstance(exc,ZeroDivisionError):

        return Response({'errmsg':'被除数不能为0'})

    if isinstance(exc,ObjectDoesNotExist):

        return Response({'errmsg':'资源不存在'})