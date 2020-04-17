from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from web import models
import random
from Utils.Tencent.sms import send_sms_single
from django_redis import get_redis_connection

class RegisterModelForm(forms.ModelForm):

    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$',"手机号格式错误")])

    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput())

    confirm_password = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput())

    code = forms.CharField(label="验证码")

    class Meta:
        model = models.UserInfo
        fields = ['username','email','password','confirm_password','mobile_phone','code']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入%s' %(field.label,)

class SendSmSForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """手机号校验的钩子"""
        mobile_phone = self.cleaned_data['mobile_phone']

        #判断短信模板是否有问题
        tpl = self.request.GET.get("tpl")
        template_id = settings.TENCENT_SMS_TEMPLATE[tpl]
        if not template_id:
            raise ValidationError("短信模板错误")

        #校验数据库中是否已有手机号
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError("手机号已存在")
        code = random.randrange(100000,999999)

        #发送短信
        sms = send_sms_single(mobile_phone,template_id,[code,])
        if sms['result']!=0:
            raise ValidationError("短信发送失败，{}".format(sms['errmsg']))

        #将验证码写入到redis(django-redis)
        conn = get_redis_connection()
        conn.set(mobile_phone,code,ex=60)

        return mobile_phone

