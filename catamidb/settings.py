from django.conf import settings

# the maximum size of the web viewable images
WEB_THUMBNAIL_SIZE = getattr(settings, 'WEB_THUMBNAIL_SIZE',
                                    (100, 75))
