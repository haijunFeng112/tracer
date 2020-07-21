import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from web.forms.file import FolderModelForm, FileModelForm
from web import models
from Utils.Tencent.cos import delete_file, delete_file_list, credential


def file(request, project_id):
    """文件列表 & 添加文件夹"""
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.File.objects.filter(id=int(folder_id), file_type=2,
                                                   project=request.tracer.project).first()

    if request.method == "GET":

        # 获取导航栏
        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent

        # 当前目录下所有的文件 & 文件夹获取
        queryset = models.File.objects.filter(project=request.tracer.project)
        if parent_object:
            # 进入某目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            # 进入根目录
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        form = FolderModelForm(request, parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrumb_list': breadcrumb_list,
            'folder_object': parent_object
        }
        return render(request, 'file.html', context)

    # 添加文件夹.
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.File.objects.filter(id=int(fid), file_type=2, project=request.tracer.project).first()

    if edit_object:
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        form = FolderModelForm(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def file_delete(request, project_id):
    """删除文件"""
    fid = request.GET.get('fid')

    # 删除数据库中的文件、文件夹、（级联删除）
    delete_object = models.File.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:

        # 删除文件，将容量还回当前项目的已使用空间
        request.tracer.project.user_space -= delete_object.file_size
        request.tracer.project.save()

        # 在cos中删除文件
        delete_file(request.tracer.project.bucket, request.tracer.project.region, delete_object.key)
        # 在数据库中删除当前文件
        delete_object.delete()
        return JsonResponse({'status': True})
    else:
        # 删除文件夹(找到文件夹下所有的文件，-数据库删除、cos文件删除、项目已使用空间返还)
        total_size = 0
        key_list = []

        folder_list = [delete_object, ]
        for folder in folder_list:
            child_list = models.File.objects.filter(project=request.tracer.project, parent=folder).order_by(
                '-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    # 文件大小z总和
                    total_size += child.file_size

                    # 删除文件
                    key_list.append({'Key': child.key})
        # cos删除文件
        if key_list:
            delete_file_list(request.tracer.project.bucket, request.tracer.project.region, key_list)
        # 删除文件，将容量还回当前项目的已使用空间
        if total_size:
            request.tracer.project.user_space -= total_size
            request.tracer.project.save()
        delete_object.delete()
        return JsonResponse({'status': True})


@csrf_exempt
def cos_credential(request, project_id):
    """获取cos上传；临时凭证"""
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024 * 1024

    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    # [{'name': '5012827_1283002439037_1024x1024soft.jpg', 'size': 111144}]
    for item in file_list:
        if item['size'] > per_file_limit:
            msg = "单文件超出限制（最大{}M），文件：{}，请升级套餐。".format(request.tracer.price_policy.per_file_size, item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']

    # request.tracer.price_policy.project_space  # 项目允许的空间
    # request.tracer.project.user_space  # 项目已使用空间
    if request.tracer.project.user_space + total_size > total_file_limit:
        return JsonResponse({'status': False, 'error': "容量超出限制，请升级套餐"})

    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({'status': True, 'data': data_dict})


@csrf_exempt
def file_post(request, project_id):
    """
    已成功上传的文件写入到数据库
    name:fileName,
    key:key,
    file_size:fileSize,
    parent:CURRENT_FOLDER_ID,
    etag:data.ETag,
    file_path:data.Location
    :param request:
    :param project_id:
    :return:
    """
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过，写入数据库
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'project': request.tracer.project, 'file_type': 1, 'update_user': request.tracer.user})
        instance = models.File.objects.create(**data_dict)

        # 项目已使用空间进行更新
        request.tracer.project.user_space += data_dict['file_size']
        request.tracer.project.save()

        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y{Y}-%m{m}-%d{d} %H:%M').format(Y='年', m='月', d='日'),
            'file_type': instance.get_file_type_display(),
            'download_url': reverse('file_download', kwargs={'project_id': project_id, 'file_id': instance.id})
        }
        return JsonResponse({'status': True, 'data': result})
    return JsonResponse({'status': False, 'data': '文件错误'})


def file_download(request, project_id, file_id):
    """下载文件"""
    import requests

    file_object = models.File.objects.filter(id=file_id,project_id=project_id).first()
    res = requests.get(file_object.file_path)

    #文件分块处理  处理大文件
    data = res.iter_content()

    #设置content_type=application/octet-stream  用于提示下载框
    response = HttpResponse(data,content_type='application/octet-stream')
    # response = HttpResponse(data)

    from django.utils.encoding import escape_uri_path

    response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(file_object.name))
    # response['Content-Disposition'] = 'attachment; filename={}'.format(file_object.name)

    return response
