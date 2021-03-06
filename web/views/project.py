from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import time
from web import models
from web.forms.project import ProjectModelForm

from Utils.Tencent.cos import create_bucket

def project_list(request):
    """项目列表"""
    if request.method == "GET":
        #GET請求查看項目列表

        """
        从数据库获取数据：
        我创建的项目：已星标、未星标
        我参与的项目：已星标、未星标
        """
        project_dict = {'star':[],'my':[],'join':[]}

        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({'value':row,'type':'my'})
            else:
                project_dict['my'].append(row)

        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({'vaule':item.project,'type':'join'})
            else:
                project_dict['join'].append(item.project)

        form = ProjectModelForm(request)
        return render(request, 'project_list.html',{'form':form,'project_dict':project_dict})

    #POST，通过ajax添加项目
    form = ProjectModelForm(request,data=request.POST)
    if form.is_valid():
        #为项目创建桶
        name = form.cleaned_data['name']
        bucket = "{}-{}-1301841574".format(request.tracer.user.mobile_phone,str(int(time.time())))
        region = 'ap-guangzhou'
        create_bucket(bucket,region)
        #验证通过：项目名、颜色、描述+creator
        form.instance.creator = request.tracer.user
        form.instance.region = region
        form.instance.bucket = bucket
        #创建项目
        instance = form.save()
        #项目初始化问题类型
        issues_type_object_list = []
        for item in models.IssuesType.PROJECT_INIT_LIST:
            issues_type_object_list.append(models.IssuesType(project=instance,title=item))
        models.IssuesType.objects.bulk_create(issues_type_object_list)
        return JsonResponse({'status': True})

    return JsonResponse({'status':False,'error':form.errors})

def project_star(request,project_type,project_id):
    #星标项目
    if project_type == 'my':
        models.Project.objects.filter(id=project_id,creator=request.tracer.user).update(star=True)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id,user=request.tracer.user).update(star=True)
        return redirect('project_list')
    return HttpResponse('请求错误')

def project_unstar(request,project_type,project_id):
    #取消星标
    if project_type == 'my':
        models.Project.objects.filter(id=project_id,creator=request.tracer.user).update(star=False)
        return redirect('project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id,user=request.tracer.user).update(star=False)
        return redirect('project_list')
    return HttpResponse('请求错误')
