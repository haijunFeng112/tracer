from django.conf.urls import url, include
from web.views import account,home,project
from web.views import manage

urlpatterns = [
    url(r'^register/$',account.register,name='register' ),
    url(r'^send/sms/$',account.sendsms,name='sendsms' ),
    url(r'^login/sms/$',account.loginsms,name='loginsms'),
    url(r'image/code/',account.image_code,name='image_code'),
    url(r'^login/$',account.login,name='login'),
    url(r'^logout/$',account.logout,name='logout'),
    url(r'^index/$',home.index,name='index'),

    #项目管理
    url(r'^project/list/$',project.project_list,name='project_list'),
    #/project/star/my/1
    #/project/star/join/1
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$',project.project_star,name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$',project.project_unstar,name='project_unstar'),

    #项目管理
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', manage.dashboard, name="dashboard"),
        url(r'^issues/$', manage.issues, name="issues"),
        url(r'^statistics/$', manage.statistics, name="statistics"),
        url(r'^file/$', manage.file, name="file"),
        url(r'^wiki/$',manage.wiki, name="wiki"),
        url(r'^setting/$', manage.setting, name="setting")
    ]),None,None),

]
# url(r'^manage/(?P<project_id>\d+)/dashboard/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/issues/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/statistics/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/file/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/wiki/$', project.project_star, name="project_star"),
# url(r'^manage/(?P<project_id>\d+)/settings/$', project.project_star, name="project_star")