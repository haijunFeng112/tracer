from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.wiki import WikiModelForm
from django.urls import reverse

def wiki(request,project_id):
    """
    wiki的首页
    :param request:
    :param project_id:
    :return:
    """
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_object = models.Wiki.objects.filter(id=wiki_id,project_id=project_id).first()

    return render(request,'wiki.html',{'wiki_object':wiki_object})

def wiki_add(request,project_id):
    """wiki添加"""
    if request.method =='GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form':form})
    form = WikiModelForm(request,data=request.POST)
    if form.is_valid():
        #判断是否选择了父文章

        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth
        else:
            form.instance.depth = 1

        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki',kwargs={'project_id':project_id})
        return redirect(url)
    return render(request, 'wiki_form.html', {'form': form})

def wiki_catalog(request,project_id):
    """wiki目录"""

    data = models.Wiki.objects.filter(project=request.tracer.project.id).values("id",'title','parent_id').order_by('depth','id')

    return JsonResponse({'status':True,'data':list(data)})

def wiki_delete(request,project_id,wiki_id):
    """删除文章"""
    models.Wiki.objects.filter(project_id=project_id,id=wiki_id).delete()

    url = reverse('wiki',kwargs={'project_id':project_id})
    return redirect(url)

def wiki_edit(request,project_id,wiki_id):
    """编辑文章"""
    wiki_object = models.Wiki.objects.filter(project_id=project_id,id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == "GET":
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})

    form = WikiModelForm(request,data=request.POST,instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth
        else:
            form.instance.depth = 1
        form.save()
        url = reverse('wiki',kwargs={'project_id':project_id})
        preview_url = "{0}?wiki_id={1}".format(url,wiki_id)

        return redirect(preview_url)

    return render(request, 'wiki_form.html', {'form': form})