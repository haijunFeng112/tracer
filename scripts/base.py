import os
import sys
import django

#测试程序
#获取项目根路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#将项目根路径添加到sys.path中
sys.path.append(base_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'Tracer.settings')
django.setup()#加载settings，使得数据库能够连接
