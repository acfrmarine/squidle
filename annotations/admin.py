__author__ = 'Lachlan Toohey'

from annotations.models import *
from django.contrib import admin
from accounts.admin_utils import GeoAdmin, Admin

admin.site.register(PointAnnotationSet, GeoAdmin)
admin.site.register(PointAnnotation, GeoAdmin)
admin.site.register(AnnotationCode, GeoAdmin)
admin.site.register(QualifierCode, GeoAdmin)
