DEBUG=True
TEMPLATE_DEBUG = True
STATIC_ROOT = '/home/auv/Code/catami_static/'



DATABASES = {
	'default': {
		'ENGINE': 'django.contrib.gis.db.backends.postgis',
		'NAME': 'catamidb',
		'USER': '$USERNAME$',
        'PASSWORD': '$PASSWORD$'
	}
}
# this hopefully will direct it all to the localhost
# and not require the full http://
GEOSERVER_URL = "/geoserver" # standard config for local host

WMS_LAYER_NAME = "catami:catamidb_images"
WMS_COLLECTION_LAYER_NAME = "catami:collection_images"

IMAGES_ROOT = '/media/data/CATAMI_SITE/media'
THUMBNAILS_SOURCE_ROOT = IMAGES_ROOT
THUMBNAILS_STORAGE_ROOT = '/media/data/CATAMI_SITE/thumbnails/'
THUMBNAILS_RESPONSE_BACKEND = 'restthumbnails.responses.apache.sendfile'
THUMBNAILS_PROXY_BASE_URL = '/thumbnails/'
THUMBNAILS_STORAGE_BASE_PATH = '/media/data/CATAMI_SITE/thumbnails/'
WEB_THUMBNAIL_SIZE = (100, 75)
STAGING_WEBIMAGE_MAX_SIZE = (None, None)

#For generic importer
STAGING_IMPORT_DIR = '/media/data/CATAMI_SITE/media'
STAGING_MOVE_ORIGINAL_IMAGES = False
STAGING_ORIGINAL_ARE_WEBIMAGES = True

## For release data importer
#STAGING_IMPORT_DIR = '/media/water/RELEASE_DATA'
#STAGING_MOVE_ORIGINAL_IMAGES = True
#STAGING_ORIGINAL_ARE_WEBIMAGES = False


STAGING_WEBIMAGE_DIR = '/media/data/CATAMI_SITE/media'


USERENA_REDIRECT_ON_SIGNOUT = '/'
USERENA_SIGNIN_AFTER_SIGNUP = True
