from django.shortcuts import render,HttpResponse
from web.forms.account import RegisterModelForm,SendSmSForm
from django.http import JsonResponse

def register(request):
    """注册"""
    form = RegisterModelForm()
    return render(request,"register.html",{'form':form})

def sendsms(request):
    """发送短信"""
    form = SendSmSForm(request,data=request.GET)
    #只校验手机号：不能为空，格式是否正确
    if form.is_valid():
        return JsonResponse({'status':True})

    return JsonResponse({'status':False,'error':form.errors})