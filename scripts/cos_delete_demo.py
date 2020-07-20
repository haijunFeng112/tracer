# -*- coding=utf-8
# appid 已在配置中移除,请在参数 Bucket 中带上 appid。Bucket 由 BucketName-APPID 组成
# 1. 设置用户配置, 包括 secretId，secretKey 以及 Region
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKIDvdCmBJ2G0VkkZ8PZkfLwHHDMGSRIwg9P'  # 替换为用户的 secretId
secret_key = '80cx4tSGxNV4QbaIRKxKWjgy5GBqNiAM'  # 替换为用户的 secretKey
region = 'ap-guangzhou'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, )
# 2. 获取客户端对象
client = CosS3Client(config)
objects = objects = {
    "Quiet": "true",
    "Object": [
        {
            "Key": "0c449273794b6f3c6d05fef0b3f5ee2e.jpg"
        },
        {
            "Key": "12066c9f9e9432f9151e4bebef5e536d.jpg"
        }
    ]
}
client.delete_objects(
    Bucket='15070311016-1594549769-1301841574',
    Delete=objects
)
