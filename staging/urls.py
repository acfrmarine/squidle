"""URL Mappings for the staging application.
"""
__author__ = 'Lachlan Toohey'

from django.conf.urls import patterns, url
#from django.contrib.auth.models import User

urlpatterns = patterns('staging.views',
                       url(r'^$', 'index', name='staging_index'),

                       # campaign creating
                       url(r'^campaign/create$', 'campaigncreate',
                           name='staging_campaign_create'),
                       url(r'^campaign/created$', 'campaigncreated',
                           name='staging_campaign_created'),

                       url(r'^browse$', 'newbrowse'),
                       url(r'^create/auv/(?P<pk>\w[\w-]*)$', 'api_auv_form',
                           name='api_auv_form')
)
