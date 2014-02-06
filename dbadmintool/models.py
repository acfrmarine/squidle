"""Models for storing the administrator bot data and report data"""

from django.db import models


class DataLogger(models.Model):
    """Holds the data for keeping track of database usage"""

    # TODO: add number of users

    collection_time = models.DateTimeField()
    num_campaigns = models.IntegerField()
    num_deployments = models.IntegerField()
    num_images = models.IntegerField()
    num_auv_deployments = models.IntegerField()
    num_bruv_deployments = models.IntegerField()
    num_dov_deployments = models.IntegerField()
    num_tv_deployments = models.IntegerField()
    num_ti_deployments = models.IntegerField()

    db_size_on_disk = models.IntegerField()
