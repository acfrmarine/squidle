"""@brief Django URLs for Report data.

Created d.marrable@ivec.org

Edits :: Name : Date : description

"""
from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^$', 'dbadmintool.views.stats_views'),
)
#    url(r'^$', 'dbadmintool.views.query_database_size'),
#                       )
