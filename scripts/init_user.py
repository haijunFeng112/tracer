import os
import sys
import django
#获取项目根路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#将项目根路径添加到sys.path中
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'Tracer.settings')
django.setup()#加载settings，使得数据库能够连接

from web import models
#向数据库中插入数据
models.UserInfo.objects.create(username="张三",email='zhangsan@qq.com',mobile_phone='19979049038',password='zhangsan')
