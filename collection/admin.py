__author__ = 'mat'

from collection.models import *
from django.contrib import admin
from accounts.admin_utils import GeoAdmin, Admin

admin.site.register(Collection, GeoAdmin)
