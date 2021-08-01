
from fdfs_client.client import Fdfs_client

conn = Fdfs_client('client.conf')

res = conn.upload_by_filename('1.jpeg')

print(res,type(res))