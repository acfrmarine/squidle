from django.conf import settings

# the staging area - where we search for deployments to import
STAGING_IMPORT_DIR = getattr(settings, 'STAGING_IMPORT_DIR',
                             '/media/catami_staging/uploadeddeployments/')

# web image directory - where compressed deployment images are served from
IMAGES_ROOT = getattr(settings, 'IMAGES_ROOT',
                      '/media/catami_live/importedimages/')
# if not defined on its own use images root as the default.
STAGING_WEBIMAGE_DIR = getattr(settings, 'STAGING_WEBIMAGE_DIR', IMAGES_ROOT)

# the archive directory where we put original full resolution
# uncompressed images
STAGING_ARCHIVE_DIR = getattr(settings, 'STAGING_ARCHIVE_DIR',
                              '/media/catami_tape/archiveimages/')

# should the original images be moved/deleted or not...
# also does not archive them if True
STAGING_MOVE_ORIGINAL_IMAGES = getattr(settings,
                                       'STAGING_MOVE_ORIGINAL_IMAGES', True)

# are the original images the webimages? if so use them in place
STAGING_ORIGINAL_ARE_WEBIMAGES = getattr(settings,
                                       'STAGING_ORIGINAL_ARE_WEBIMAGES', False)

# the maximum size of the web viewable images
STAGING_WEBIMAGE_MAX_SIZE = getattr(settings, 'STAGING_WEBIMAGE_MAX_SIZE',
                                    (None, None))
