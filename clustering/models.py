"""Models for the clustering app.

Depends on Force.Image and Collection.Collection
"""
from django.db import models
from catamidb.models import Image
from collection.models import Collection

from django.core.validators import MaxValueValidator, MinValueValidator


class ClusterRun(models.Model):
    """The clustering of a Collection with a certain tuning parameter."""
    collection = models.ForeignKey(Collection)

    # Tuning parameter
    cluster_width = models.FloatField()


class ImageProbability(models.Model):
    """The probability the image belongs to a label."""
    image = models.ForeignKey(Image)
    probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    cluster_label = models.ForeignKey('ClusterLabel')


class ClusterLabel(models.Model):
    """Labels created in a particular cluster run."""
    images = models.ManyToManyField(Image, related_name='clusters')
    cluster_label = models.IntegerField()
    probabilities = models.ManyToManyField(
        Image,
        through='ImageProbability',
        related_name='cluster_probabilities',
    )
    cluster_run = models.ForeignKey(ClusterRun)
