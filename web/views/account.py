
from django.shortcuts import render,HttpResponse,redirect
import uuid
import datetime
from web import models
from web.forms.account import RegisterModelForm,SendSmSForm,LoginSmSForm,LoginForm
from django.http import JsonResponse

def register(request):
    """注册"""
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request,"register.html",{'form':form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        #验证通过，写入数据库(密码要密文)
        instance = form.save()

        #创建交易记录
        policy_object =  models.PricePolicy.objects.filter(category=1,title='个人免费版').first()

        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user = instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime= datetime.datetime.now()

        )

        return JsonResponse({'status':True,'data':'/login/'})

    return JsonResponse({'status':False,'error':form.errors})

def sendsms(request):
    """发送短信"""
    form = SendSmSForm(request,data=request.GET)
    #只校验手机号：不能为空，格式是否正确
    if form.is_valid():
        return JsonResponse({'status':True})

    return JsonResponse({'status':False,'error':form.errors})

def loginsms(request):
    """短信登录"""
    if request.method =="GET":
        form = LoginSmSForm()
        return render(request,"loginSmS.html",{'form':form})
    form = LoginSmSForm(data=request.POST)
    if form.is_valid():
        user_object = form.cleaned_data['mobile_phone']

        #把用户名写到session中
        request.session['user_id'] = user_object.id
        #用户输入正确，登录成功
        return JsonResponse({"status":True,"data":"/index/"})
    return JsonResponse({'status':False,'error':form.errors})

def login(request):
    """用户名和密码登录"""
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request,'login.html',{'form':form})
    form = LoginForm(request,request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        from django.db.models import Q

        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(mobile_phone = username)).filter(
            password=password).first()
        if user_object:
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60*60*24*14)
            #用户名密码正确
            return redirect("index")
        form.add_error('username','用户名或密码错误')
    return render(request,'login.html',{'form':form})

def logout(request):
    request.session.flush()
    return redirect('index')

def image_code(request):
    """生成图片验证码"""
    from io import BytesIO
    from Utils.image_code import check_code

    image_object,code = check_code()

    request.session['image_code'] = code #将验证码放入session中
    request.session.set_expiry(60) #主动修改session的过期时间为60秒

    stream = BytesIO()
    image_object.save(stream,'png')

    return HttpResponse(stream.getvalue())