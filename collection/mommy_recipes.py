from datetime import datetime
from django.contrib.gis.geos import Point
from django.db.models import ManyToManyField
from model_mommy.recipe import Recipe
from catamidb.models import Image
from collection import models
from collection.models import Collection

collection1 = Recipe(
    Collection,
    creation_date=datetime.now(),
    modified_date=datetime.now(),
    #images = ManyToManyField(Image, related_name='collections')
)

collection2 = Recipe(
    Collection,
    creation_date=datetime.now(),
    modified_date=datetime.now(),
    #images = ManyToManyField(Image, related_name='collections')
)

collection3 = Recipe(
    Collection,
    creation_date=datetime.now(),
    modified_date=datetime.now(),
    #images = ManyToManyField(Image, related_name='collections')
)