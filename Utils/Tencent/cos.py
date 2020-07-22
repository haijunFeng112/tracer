from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
from django.conf import settings
from qcloud_cos.cos_exception import CosServiceError

def create_bucket(bucket,region="ap-guangzhou"):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 区域
    :return:
    """
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)


    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    # 2. 获取客户端对象
    client = CosS3Client(config)

    client.create_bucket(
        Bucket=bucket,
        ACL="public-read"
    )

    cors_config = {
        'CORSRule':[
            {
                'AllowedOrigin':'*',
                'AllowedMethod':['GET','PUT','HEAD','POST','DELETE'],
                'AllowedHeader':'*',
                'ExposeHeader':'*',
                'MaxAgeSeconds':500
            }
        ]
    }

    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )

def upload_file(bucket,region,file_object,key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )

    # 2. 获取客户端对象
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,
        Key=key,
    )

    # https: // fenghaijun - 1301841574.cos.ap - guangzhou.myqcloud.com / picture.jpg

    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket,region,key)

def delete_file(bucket,region,key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )

    # 2. 获取客户端对象
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key,
    )

def delete_file_list(bucket,region,key_list):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )

    # 2. 获取客户端对象
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object":key_list
    }


    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )

def credential(bucket,region):
    """获取cos上传临时凭证"""

    from sts.sts import Sts

    config = {
        #临时秘钥有效时长，单位为秒
        'duration_seconds':1800,
        'secret_id':settings.TENCENT_COS_ID,
        'secret_key':settings.TENCENT_COS_KEY,
        'bucket':bucket,
        'region':region,
        'allow_prefix':'*',
        'allow_actions':[
            '*'
        ]
    }
    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict

def check_file(bucket,region,key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )

    # 2. 获取客户端对象
    client = CosS3Client(config)

    data = client.head_object(
        Bucket=bucket,
        Key=key,
    )

    return data

def delete_bucket(bucket,region):
    """删除桶"""
    #删除桶文件、桶碎片、桶
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    # 2. 获取客户端对象
    client = CosS3Client(config)

    try:
        #删除文件
        while True:
            part_objects = client.list_objects(bucket)
            #检测是否删除完毕
            contents = part_objects.get('Contents')
            if not contents:
                break

            #批量删除
            objects = {
                "Quiet": "true",
                "Object": [{'Key':item["Key"]} for item in contents]
            }
            client.delete_objects(bucket,objects)

            if part_objects['IsTruncated'] == 'false':
                break
        #找到碎片删除
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket,item['Key'],item['UploadId'])
            if part_uploads['IsTruncated'] == 'false':
                break

        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass