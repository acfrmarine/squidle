"""URL Mappings for the webinterface application.
"""
from catamidb import authorization
from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()


admin.autodiscover()

#configure initial auth and groups
authorization.on_startup_configuration()

urlpatterns = patterns(
    'webinterface.views',
    url(r'^$', 'index', name='index'),

    ##Info Pages
    #url(r'^faq', 'faq'),
    #url(r'^contact', 'contact'),
    #url(r'^howto', 'howto'),
    #url(r'^about', 'about'),
    #url(r'^proxy/$', 'proxy'),

    #url(r'^explore$', 'explore'),
    #
    #url(r'^explore_campaign/(?P<campaign_id>\d+)/$',
    #    'explore_campaign'),

    url(r'^explore/getmapextent$',
        'get_multiple_deployment_extent'),

    url(r'^geoserverstyle$', 'dynamic_style'),
    url(r'^geoserverSimplestyle$', 'dynamic_Simplestyle'),
    url(r'^geoserverDeploymentstyle$', 'dynamic_Deploymentstyle'),
    url(r'^geoserverDeploymentSimplestyle$', 'dynamic_DeploymentSimplestyle'),
    url(r'^geoservercolourmap$', 'dynamic_colourmap'),

    #url(r'^viewcollection$', 'viewcollection'),

    #Staging
    url(r'^staging/', include('staging.urls')),

    # Projects
    #url(r'^projects$', 'projects'),

    #Collection detail Views
    #url(r'^collections/(?P<collection_id>\d+)/$', 'view_collection'),
    #url(r'^project$', 'view_project'),
#    url(
#        r'^collections/(?P<collection_id>\d+)/workset/(?P<workset_id>\d+)/$',
#        'view_workset'),
    #url(r'^my_collections$', 'my_collections'),
    #url(r'^my_collections_all$', 'my_collections_all'),
    #url(r'^my_collections_recent$', 'my_collections_recent'),
    #url(r'^public_collections$', 'public_collections'),
    #url(r'^public_collections_all$', 'public_collections_all'),
    #url(r'^public_collections_recent$', 'public_collections_recent'),

    # NEW VIEWS #########################################################
    url(r'^viewproject$', 'project'),
    #url(r'^viewmap$', 'map'),
    url(r'^download_csv$','download_csv'),

    url(r'^update_classes$','update_classes_gspread'),

    url(r'^get_extents$','get_extents'),
    url(r'^loggedout$','loggedout'),
    url(r'^citizenscience/(?P<citizen_project>\w+)/loggedout$', 'loggedout'),

    url(r'^citizenscience$','citizenscience_chooseproject'),
    url(r'^citizenscience/(?P<citizen_project>\w+)/$', 'index', name='index'),
    url(r'^citizenscience/(?P<citizen_project>\w+)/viewproject$', 'project'),
    url(r'^citizenscience/(?P<citizen_project>\w+)/citizenscience_labels$','citizenscience_getlabels'),

    url(r'^get_annotation_info','get_annotation_info'),
    url(r'^citizenscience/(?P<citizen_project>\w+)/get_annotation_info','get_annotation_info'),


    #####################################################################

    #Collection Object Views
    url(r'^view_subset$', 'view_subset'),
    url(r'^all_subsets/(?P<collection_id>\d+)/$',
        'all_subsets'),
    url(r'^my_subsets$', 'my_subsets'),
    url(r'^public_subsets$', 'public_subsets'),
    url(r'^imageview$', 'image_view'),
#    url(r'^imageannotate$', 'image_annotate'),
    url(r'^imageannotate/(?P<image_id>\d+)/$', 'image_annotate'),
    url(r'^imageedit$', 'image_edit'),

    #Collection Management
    #url(r'^collections/create/$',
    #    'create_collection_from_deployments'),
    url(r'^collections/create/$', 'create_collection_from_explore'),
    url(r'^collections/getcollectionextent$', 'get_collection_extent'),

    #plain data views
    url(r'^data/$', 'data'),
    url(r'^data/auvdeployments/$', 'auvdeployments'),
    url(r'^data/auvdeployments/map/$',
        'auvdeployments_map'),
    url(r'^data/auvdeployments/(?P<auvdeployment_id>\d+)/$',
        'auvdeployment_detail'),

    url(r'^data/deployments/$', 'deployments'),
    url(r'^data/deployments/map/$', 'deployments_map'),

    url(r'^data/campaigns/$', 'campaigns'),
    url(r'^data/campaigns/(?P<campaign_id>\d+)/$',
        'campaign_detail'),

    #API docs
    url(r'^api/', include('jsonapi.urls')),

    #dbadmin tool
    url(r'^report/', include('dbadmintool.urls')),

    # userena
    (r'^accounts/', include('accounts.urls')),

    # Dajaxice
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #admin interface
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns(
    '',
    url(r'^accounts/login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'}),
    # the raw original images
    url(r'^{0}/(?P<path>.*)$'.format(settings.IMAGES_URL),
        'django.views.static.serve',
        {'document_root': settings.IMAGES_ROOT,
         'show_indexes': False}),
    # and the thumbnails...
    url(r'^thumbnails/', include('restthumbnails.urls')),
)
