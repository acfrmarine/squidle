"""Feature models."""
from django.db import models
from catamidb.models import Image


class ImageFeature(models.Model):
    """Extends Force.Image to include feature arrays

    for clustering and classification"""

    image = models.OneToOneField(Image)
    feature_file = models.CharField(max_length=200)
