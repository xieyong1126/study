
from django.views import View
from goods.models import SKU,GoodsCategory
from django.core.paginator import Paginator
from django.http import JsonResponse
from .utils import get_breadcrumb
from django.conf import settings

class ListView(View):

    def get(self, request, category_id):
        # 1、提取参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')

        # 2、校验参数
        # 无需校验查询字符串参数

        # 3、数据处理
        # 3.1 根据category_id查询出所有的sku商品
        skus = SKU.objects.filter(
            category_id=category_id
        ).order_by(ordering)

        # 3.2 分页 —— page、page_size
        # Paginator(object_list, per_page): object_list是模型类查询集，per_page指每页几个
        paginator = Paginator(skus, per_page=page_size)
        # paginator.count属性，记录被分页数据的总数
        # paginator.num_pages属性，记录分到的总页数
        # paginator.per_page属性，记录是按照每页几个划分

        # page(number): number表示取第几页
        # 返回值是当前页对象
        page = paginator.page(page)
        # page.object_list属性，记录当前页中的查询集
        # page.num属性，记录当前是第几页

        sku_list = []
        for sku in page.object_list:
            # sku是SKU商品模型类对象
            sku_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image_url.url,
                'name': sku.name,
                'price': sku.price
            })


        # breadcrumb = {
        #     "cat1": "手机",
        #     "cat2": "手机通信",
        #     "cat3": "手机"
        # }
        category = GoodsCategory.objects.get(pk=category_id)
        breadcrumb = get_breadcrumb(category)

        # 4、构建响应
        return JsonResponse({
            'code':0 ,
            'errmsg': 'ok',
            'count': paginator.num_pages, # 总页数
            'list': sku_list,
            'breadcrumb': breadcrumb
        })


class HotGoodsView(View):

    def get(self, request, category_id):

        # 1、根据分类id，获取sku商品，根据销量排序，取前2
        skus = SKU.objects.filter(
            category_id=category_id,
            is_launched=True
        ).order_by('-sales')[:2]

        # 2、构造响应数据返回
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image_url.url,
                'name': sku.name,
                'price': sku.price
            })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'hot_skus': hot_skus
        })



# SearchView: haystack自己的一个视图对应接口如下
# 请求方式：GET
# 请求路径：/search/
# 请求参数：查询字符串q
# 响应数据：此处我们自己构建响应
from haystack.views import SearchView

class MySearchView(SearchView):

    def create_response(self):
        """
        重写，自定义返回JsonResponse
        :return:
        """
        # 获取搜索结果
        data = self.get_context()
        # data['query']: 用户搜索词
        # data['page']: django分页对象——当前页
        # data['page'].object_list分页结果,是SearchResult对象；SearchResult.object属性是对应SKU对象
        # data['paginator']: django分页器对象

        # es搜索的结果——sku对象转化而成的字典！
        data_list = []
        for result in data['page'].object_list:
            # result: 是SearchResult对象
            # result.object：是sku对象
            data_list.append({
                'id': result.object.id,
                'name': result.object.name,
                'price': result.object.price,
                'default_image_url': result.object.default_image_url.url,
                'searchkey': data['query'],
                'page_size': data['paginator'].per_page, # 每页数量
                'count': data['paginator'].count # 搜索的结果总数
            })

        # 默认JsonResponse只能传入字典，如果传入列表必须设置safe=False
        return JsonResponse(data_list, safe=False)




























