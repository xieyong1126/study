

from itsdangerous import TimedJSONWebSignatureSerializer,BadData,SignatureExpired
from django.conf import settings


# 1、对openid加密
def generate_access_token(openid):

    serializer = TimedJSONWebSignatureSerializer(
        secret_key=settings.SECRET_KEY,
        expires_in=3600
    )

    # 对 {"openid": openid} 进行加密
    token = serializer.dumps({
        'openid': openid
    })

    return token.decode()


# 2、对openid解密
def check_access_token(token):

    serializer = TimedJSONWebSignatureSerializer(
        secret_key=settings.SECRET_KEY
    )

    try:
        payload = serializer.loads(token)
    except BadData as e:
        print(e)
        return None

    return payload.get('openid')
