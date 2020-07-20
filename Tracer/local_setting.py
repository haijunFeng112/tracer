LANGUAGE_CODE = 'zh-hans'

#腾讯云短信应用的app_id
TENCENT_SMS_APP_ID = 1400349756
#腾讯云短信应用的app_key
TENCENT_SMS_APP_KEY = "284b35a0669cf8bc56afc90bace7a0e7"
#腾讯云短信签名内容
TENCENT_SMS_SIGN = "小毛孩"
#腾讯云短信模板信息
TENCENT_SMS_TEMPLATE = {
    'reset':577436,
    'login':577432,
    'register':577434
}
TENCENT_COS_ID="AKIDvdCmBJ2G0VkkZ8PZkfLwHHDMGSRIwg9P"
TENCENT_COS_KEY="80cx4tSGxNV4QbaIRKxKWjgy5GBqNiAM"

#redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379", # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": "foobared" # redis密码
        }
    }
}