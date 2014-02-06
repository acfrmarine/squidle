"""Admin interface for catamidb models."""
from django.contrib.auth.models import User, Group
from catamiPortal import settings

__author__ = 'mat'

from catamidb.models import *
from django.contrib import admin
from accounts.admin_utils import GeoAdmin, Admin
from guardian.shortcuts import assign
import logging

logger = logging.getLogger(__name__)

admin.site.register(Campaign, GeoAdmin)
admin.site.register(Deployment, GeoAdmin)
admin.site.register(Pose, GeoAdmin)
admin.site.register(Camera, Admin)
admin.site.register(Image, Admin)
admin.site.register(ScientificPoseMeasurement, Admin)
admin.site.register(ScientificImageMeasurement, Admin)
admin.site.register(ScientificMeasurementType, Admin)

admin.site.register(AUVDeployment, GeoAdmin)
admin.site.register(BRUVDeployment, GeoAdmin)
admin.site.register(DOVDeployment, GeoAdmin)
admin.site.register(TVDeployment, GeoAdmin)
admin.site.register(TIDeployment, GeoAdmin)
