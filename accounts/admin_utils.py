from guardian.admin import GuardedModelAdmin
from django.contrib.gis.admin import GeoModelAdmin

class Admin(GuardedModelAdmin):
    pass

class GeoAdmin(Admin, GeoModelAdmin):
    pass

