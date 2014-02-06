from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

urlpatterns = patterns('feedback.views',
    url(r'^add$', 'add'),
    url(r'^list$', 'request_list'),
    url(r'^view/(?P<pk>\d+)$', 'view'),
    url(r'^edit/(?P<pk>\d+)$', 'edit'),
    url(r'^delete/(?P<pk>\d+)$', 'delete'),
)
