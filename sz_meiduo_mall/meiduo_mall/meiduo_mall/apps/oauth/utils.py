from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings
from itsdangerous import BadData

def generate_access_token(openid):
    # 创建对象  (秘钥，有效期（秒）)
    serilizer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,600)

    data = {'openid':openid}

    token = serilizer.dumps(data).decode()

    return token

def check_access_token(access_token):
    serilizer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 600)
    try:
        # 尝试使用对象的 loads 函数
        # 对 access_token 进行反序列化( 类似于解密 )
        # 查看是否能够获取到数据
        data = serilizer.loads(access_token)
    except BadData:
        # 如果出错, 则说明 access_token 里面不是我们认可的.
        # 返回 None
        return None
    else:
        openid = data.get('openid')
        return openid



