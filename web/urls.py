from django.conf.urls import url
from web.views import account,home

urlpatterns = [
    url(r'^register/$',account.register,name='register' ),
    url(r'^send/sms/$',account.sendsms,name='sendsms' ),
    url(r'^login/sms/$',account.loginsms,name='loginsms'),
    url(r'image/code',account.image_code,name='image_code'),
    url(r'^login/$',account.login,name='login'),
    url(r'^logout/$',account.logout,name='logout'),
    url(r'^index/$',home.index,name='index')
]
