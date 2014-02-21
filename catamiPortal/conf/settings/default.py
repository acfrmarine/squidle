import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
import socket
# Django settings for catamiPortal project.


SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

DEBUG = False
TEMPLATE_DEBUG = False
TASTYPIE_FULL_DEBUG = False

POSTGIS_VERSION = (1, 5, 2)
SOUTH_TESTS_MIGRATE = False # To disable migrations and use syncdb instead
SKIP_SOUTH_TESTS = True # To disable South's own unit tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    #    '--cover-package=catamidb,accounts,clustering,collection,dbadmintool,features,staging,webinterface'
    #    '--coverage-exclude=../*migrations*'
]

WMS_URL = "http://localhost:8080/geoserver/wms" # standard config for local host
WMS_LAYER_NAME = "catami:catamidb_images"
WMS_COLLECTION_LAYER_NAME = "catami:collection_images"

ADMINS = (
    ('Ariell Friedman', 'a.friedman@acfr.usyd.edu.au'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'catamidb', # Or path to database file if using sqlite3.
        'USER': 'pocock', # Not used with sqlite3.
        'PASSWORD': 'qwer789ASDF456zxcv123', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Australia/Sydney'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-au'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# dont have slashes at either end, they are automatically added
IMAGES_URL = 'images'
IMAGES_ROOT = '/media/catami_live/importedimages'

THUMBNAILS_SOURCE_ROOT = IMAGES_ROOT
THUMBNAILS_STORAGE_ROOT = '/media/catami_live/thumbnailimages'
THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.apache.sendfile'
WEB_IHUMBNAIL_SIZE = (100, 75)
STAGING_WEBIMAGE_MAX_SIZE = (1500, 1500)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/catami/media/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder', # Dajaxice
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd7jk#mjzc!qsz*+j)lnx*j0f+g%a0bej-n=&amp;0)7&amp;g=n!^1iaaf'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader', # Dajaxice
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'waffle.middleware.WaffleMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'webinterface.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'catamiPortal.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'catamiPortal/templates')
)

FIXTURE_DIRS = (os.path.join(SITE_ROOT, 'catamidb/fixtures'))

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ''
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.gis',
    'catamidb',
    'staging',
    'jsonapi',
    'webinterface',
    'django_jenkins',
    'dbadmintool',
    'features',
    'south',
    'django_coverage',
    'accounts',
    'collection',
    'guardian',
    'easy_thumbnails',
    'restthumbnails',
    'django_nose',
    'clustering',
    'annotations',
    'tastypie',
    'userena',
    'waffle',
    'dajaxice',
    'dajax',
    'bootstrap_toolkit',
    'feedback',
)
#    'haystack', # disabled 16th Jan 2013


#tasks that jenkins will run on the build server
JENKINS_TASKS = {
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.django_tests'
}

PROJECT_APPS = (
    'catamidb',
    'staging',
    'webinterface',
    'dbadmintool',
    'accounts',
    'annotations',
    'collection',
    'features',
    'jsonapi',
    'clustering',
)

#haystack support
#HAYSTACK_CONNECTIONS = {
#    'default': {
#        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#        'URL': 'http://127.0.0.1:8983/solr'
#    },
#}

ANONYMOUS_USER_ID = -1

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'none@none.none'
#EMAIL_HOST_PASSWORD = 'none'
#AUTH_PROFILE_MODULE = "accounts.UserProfile"
AUTH_PROFILE_MODULE = 'accounts.MyProfile'

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'

USERENA_ACTIVATION_REQUIRED = 0

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': os.path.join(SITE_ROOT, 'log/catamiPortal.log')
        }
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'staging': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'webinterface': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'catamiPortal': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'dbadmintool': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'catamidb': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'features': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },

    }
}
