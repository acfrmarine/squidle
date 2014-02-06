from guardian.models import *
from django.contrib import admin
from accounts.admin_utils import GeoAdmin, Admin

admin.site.register(UserObjectPermission)
admin.site.register(GroupObjectPermission)
admin.site.register(Permission)
