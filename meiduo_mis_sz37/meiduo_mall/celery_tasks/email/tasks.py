
# 只有我们配置好环境变量DJANGO_SETTINGS_MODULE，以下两行导包才能够找到django配置文件
# 然后加载配置文件中的配置项
from django.core.mail import send_mail
from django.conf import settings


from celery_tasks.main import celery_app


@celery_app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):

    subject = '美多邮箱验证'

    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    send_mail(
        subject,
        '',  # 普通文本邮件内容
        from_email=settings.EMAIL_FROM,
        recipient_list=[to_email],
        html_message=html_message
    )