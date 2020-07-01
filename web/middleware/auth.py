import datetime

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from web import models
from django.conf import settings

class Tracer():
    def __init__(self):
        self.user = None
        self.price_policy = None

class AuthMiddleware(MiddlewareMixin):


    def process_request(self,request):
        """如果用户已登录，则request中赋值"""

        request.tracer = Tracer()

        user_id = request.session.get('user_id',0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer.user=user_object

        #白名单：没有登录也可以访问的url
        """
        1.获取当前用户访问的URL
        2.检查URL是否在白名单中,如果在则可以继续访问，如果不在则进行判断是否已登录
        """
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        if not request.tracer.user:
            return redirect('login')

        #登录成功之后，访问后台管理时：获取当前用户所拥有的的额度
        #方式一：免费额度在交易记录中存储
        #获取当前用户id最大(最近交易记录)
        _object = models.Transaction.objects.filter(user=user_object,status=2).order_by("-id").first()
        #ban断是否已过期
        current_datetime = datetime.datetime.now()
        if _object.end_datetime and _object.end_datetime < current_datetime:
            _object = models.Transaction.objects.filter(user=user_object,status=2,price_policy_category=1).first()
        # request.transaction = _object
        request.tracer.price_policy = _object.price_policy