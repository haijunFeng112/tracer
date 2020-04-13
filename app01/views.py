
from django.shortcuts import render,HttpResponse
from Utils.Tencent.sms import send_sms_single
from random import randrange
from django.conf import settings

# Create your views here.
def send_sms(request):
    """
    发送短信
    :param request:
    :return:
    """
    tpl = request.GET.get("tpl")
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        return HttpResponse("模板不存在")
    code = randrange(100000,999999)
    res = send_sms_single("15070311016",template_id,[code,])
    print(res)
    return HttpResponse("成功")

from django import forms
from app01 import models
from django.core.validators import RegexValidator
class RegisterModelForm(forms.ModelForm):

    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$)',"手机号格式错误")])

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
def register(request):
    form = RegisterModelForm()
    return render(request,'register.html',{'form':form})
