"""
自定义文件存储后端，使得我们的image.url得出的结果前面拼接完整的fdfs请求url前缀
"""

# Storage：存储后端基类
from django.core.files.storage import Storage
from django.conf import settings
from rest_framework.serializers import ValidationError
from fdfs_client.client import Fdfs_client

class FastDFSStorage(Storage):

    def open(self, name, mode='rb'):
        # 如果需要把上传的文件存储django本地，则需要在本地打开一个文件
        return None # 把图片上传fdfs，不是保存本地


    def save(self, name, content, max_length=None):
        # 保存文件逻辑：把文件上传到fdfs服务器上
        # ret = {
        #     'Group name': 'Storage中组名',
        #     'Remote file_id': '文件保存的位置',
        #     'Status': '文件上传结果(成功还是失败)',
        #     'Local file name': '上传文件的路径',
        #     'Uploaded size': '上传文件的大小',
        #     'Storage IP': 'Storage服务器的ip地址'
        # }
        # name是⽂文件名
        # content是上传的⽂文件被封装成的⽂文件对象
        # 调⽤用fdfs客户端接⼝口实现⽂文件上传到fdfs
        conn = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')

        res = conn.upload_by_buffer(content.read())
        if res['Status'] !='Upload successed.':
            #说明上传成功
            raise ValidationError
        #fdfs文件标识，需要存储到mysql
        file_id = res['Remote file_id']
       # print(file_id)
        return file_id


    def url(self, name):
        # 该函数决定了，ImageField.url的结果
        # name: 当前字段在数据库中存储的值
        # name = group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429
        # "http://image.meiduo.site:8888/" + name
        return settings.FDFS_URL + name

    def exists(self, name):

    # ⽤用于判断⽂文件是否重复保存
    # return True # ⽂文件已经存在
    # 当前业务返回False，表示"⽂文件不不保存本地，直接调⽤用后续的save⽅方法实现上传fdfs"
        return False  # ⽂文件不不存在