"""@brief Django URLs for main Catami views.

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'catamiPortal.views.home', name='home'),
                       # url(r'^catamiPortal/', include('catamiPortal.foo.urls')),

                       url(r'^$', 'catamiPortal.views.index'),
                       url(r'^api/', include('jsonapi.urls')),
                       url(r'^faq', 'catamiPortal.views.faq'),
                       url(r'^contact', 'catamiPortal.views.contact'),
                       url(r'^attribution', 'catamiPortal.views.attribution'),
                       url(r'^proxy/(?P<url>.*)$', 'catamiPortal.views.proxy'),


                       url(r'^staging/', include('staging.urls')),

                       url(r'images/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.IMAGES_ROOT, 'show_indexes': True}),

                       url(r'^webinterface/', include('webinterface.urls')),

                       #to hide the database name
                       url(r'^data/', include('Force.urls')),

                       #haystack
                       #url(r'^search/', include('haystack.urls')),

                       # plots
                       url(r'^report/', include('dbadmintool.urls')),

                       # userena
                       (r'^accounts/', include('accounts.urls')),

                       #dbadmin tool

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login',
                           {'template_name': 'registration/login.html'}),
                       url(r'^logout/$', 'catamiPortal.views.logout_view'),
)
