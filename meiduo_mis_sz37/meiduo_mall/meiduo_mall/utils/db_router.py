"""
自定义Django数据库路由后端
"""

class MasterSlaveDBRouter(object):

    # 重写里面的一些方法来指定：写到"default"，从"slave"中读

    def db_for_read(self, *args, **kwargs):
        # 从slave配置指向的从mysql读
        return "slave"


    def db_for_write(self, *args, **kwargs):
        # 写入default配置指向的主mysql
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        # 允许关联操作
        return True