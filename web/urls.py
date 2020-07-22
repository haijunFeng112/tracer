from django.conf.urls import url, include
from web.views import account, home, project
from web.views import manage
from web.views import wiki
from web.views import file
from web.views import setting

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^send/sms/$', account.sendsms, name='sendsms'),
    url(r'^login/sms/$', account.loginsms, name='loginsms'),
    url(r'image/code/', account.image_code, name='image_code'),
    url(r'^login/$', account.login, name='login'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^index/$', home.index, name='index'),

    # 项目管理
    url(r'^project/list/$', project.project_list, name='project_list'),
    # /project/star/my/1
    # /project/star/join/1
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    # 项目管理
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name="dashboard"),
        url(r'^issues/$', manage.issues, name="issues"),
        url(r'^statistics/$', manage.statistics, name="statistics"),

        url(r'^wiki/$', wiki.wiki, name="wiki"),
        url(r'^wiki/add/$', wiki.wiki_add, name="wiki_add"),
        url(r'^wiki/catalog/$', wiki.wiki_catalog, name="wiki_catalog"),
        url(r'^wiki/delete/(?P<wiki_id>\d+)$', wiki.wiki_delete, name="wiki_delete"),
        url(r'^wiki/edit/(?P<wiki_id>\d+)$', wiki.wiki_edit, name="wiki_edit"),
        url(r'^wiki/upload/$', wiki.wiki_upload, name="wiki_upload"),

        url(r'^file/$', file.file, name="file"),
        url(r'^file/delete$', file.file_delete, name="file_delete"),
        url(r'^cos/cos_credential$', file.cos_credential, name="cos_credential"),
        url(r'^file/post$', file.file_post, name="file_post"),
        url(r'^file/download/(?P<file_id>\d+)$', file.file_download, name="file_download"),

        url(r'^setting/$', setting.setting, name="setting"),
        url(r'^setting/delete/$', setting.delete, name="setting_delete")
    ]), None, None),

]
# url(r'^manage/(?P<project_id>\d+)/dashboard/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/issues/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/statistics/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/file/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/wiki/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/settings/$', project.project_star, name="project_star")
