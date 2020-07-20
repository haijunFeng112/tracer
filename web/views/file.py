from django.http import JsonResponse
from django.shortcuts import render
from web.forms.file import FolderModelForm
from web import models
from Utils.Tencent.cos import delete_file,delete_file_list


def file(request, project_id):
    """文件列表 & 添加文件夹"""
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.File.objects.filter(id=int(folder_id), file_type=2,
                                                   project=request.tracer.project).first()

    if request.method == "GET":

        #获取导航栏
        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0,{'id':parent.id,'name':parent.name})
            parent = parent.parent

        #当前目录下所有的文件 & 文件夹获取
        queryset = models.File.objects.filter(project=request.tracer.project)
        if parent_object:
            #进入某目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            #进入根目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        form = FolderModelForm(request, parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrumb_list':breadcrumb_list
        }
        return render(request, 'file.html', context)

    # 添加文件夹.
    fid = request.POST.get('fid','')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.File.objects.filter(id=int(fid),file_type=2,project=request.tracer.project).first()

    if edit_object:
        form = FolderModelForm(request,parent_object,data=request.POST,instance=edit_object)
    else:
        form = FolderModelForm(request,parent_object,data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})

def file_delete(request,project_id):
    """删除文件"""
    fid = request.GET.get('fid')

    #删除数据库中的文件、文件夹、（级联删除）
    delete_object = models.File.objects.filter(id=fid,project=request.tracer.project).first()
    if delete_object.file_type == 1:

        #删除文件，将容量还回当前项目的已使用空间
        request.tracer.project.user_space -= delete_object.file_size
        request.tracer.project.save()

        #在cos中删除文件
        delete_file(request.tracer.project.bucket,request.tracer.project.region,delete_object.key)
        #在数据库中删除当前文件
        delete_object.delete()
        return JsonResponse({'status': True})
    else:
        #删除文件夹(找到文件夹下所有的文件，-数据库删除、cos文件删除、项目已使用空间返还)
        total_size = 0
        key_list = []

        folder_list = [delete_object,]
        for folder in folder_list:
            child_list = models.File.objects.filter(project=request.tracer.project,parent=folder).order_by('-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    #文件大小z总和
                    total_size += child.file_size

                    #删除文件
                    key_list.append({'Key':child.key})
        #cos删除文件
        if key_list:
            delete_file_list(request.tracer.project.bucket,request.tracer.project.region,key_list)
         # 删除文件，将容量还回当前项目的已使用空间
        if total_size:
            request.tracer.project.user_space -= total_size
            request.tracer.project.save()
        delete_object.delete()
        return JsonResponse({'status':True})