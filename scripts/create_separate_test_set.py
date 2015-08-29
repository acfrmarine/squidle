__author__ = 'mbewley'

import sys
import os
from sklearn.cross_validation import train_test_split
import numpy as np

sys.path.append('/home/auv/git/squidle-playground')
sys.path.append('/home/auv/git')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from annotations.models import Collection, PointAnnotationSet
from collection.authorization import apply_collection_permissions
from catamidb.models import Image
from django.contrib.auth.models import User

user = User.objects.get(id=61)

proj = Collection.objects.get(name='AUSBEN2014')
subsets = Collection.objects.filter(parent__exact=proj)
ann_sets = PointAnnotationSet.objects.filter(collection__in=subsets)

proj_test = Collection.objects.get_or_create(
    name='AUSBEN2014_test',
    description='Australian',
    owner=user,
    creation_info="Imported CPC labels",
    is_locked=False
)[0]
proj_test.save()
apply_collection_permissions(user=user, collection=proj)

# Move all images back from the test set to the original
for subset in subsets:
    # Make a copy of this subset in the test set project
    subset_test = Collection.objects.get_or_create(
        name=subset.name,
        description=subset.description,
        owner=user,
        parent=proj_test,
        creation_info="Imported CPC labels",
        is_locked=False
    )[0]
    # subset_test.save()
    print Image.objects.filter(collections__exact=subset).count(),
    print Image.objects.filter(collections__exact=subset_test).count()

    # test_images = Image.objects.filter(collections__exact=subset_test)
    # # [subset.images.add(im) for im in test_images]
    # [subset_test.images.remove(im) for im in test_images]
    #
    # print Image.objects.filter(collections__exact=subset).count(),
    # print Image.objects.filter(collections__exact=subset_test).count()

# for subset in subsets:
#     # Make a copy of this subset in the test set project
#     subset_test = Collection.objects.get_or_create(
#         name=subset.name,
#         description=subset.description,
#         owner=user,
#         parent=proj_test,
#         creation_info="Imported CPC labels",
#         is_locked=False
#     )[0]
#     subset.save()


# # Subselect a random 15% of the images from the subset, to use as a test set.
#     images = Image.objects.filter(collections__exact=subset)
#     img_ids = np.array(images.values_list('id')).ravel()
#     img_ids_train, img_ids_test = train_test_split(img_ids, test_size=0.15, random_state=0)
#     images_test = Image.objects.filter(id__in=img_ids_test.tolist())
#
#     # Remove the images from the original subset
#     for img in images_test:
#         subset_test.images.add(img)
#         if img in subset_test.images.all():
#             subset.images.remove(img)
#
#             # It worked!
#             assert img in subset_test.images.all()
#             assert img not in subset.images.all()
#         else:
#             subset_test.images.remove(img)
#
#             # It failed :-(
#             assert img not in subset_test.images.all()
#             assert img in subset.images.all()

    ann_set = PointAnnotationSet.objects.get(collection__exact=subset)
    print subset, ann_set

    # Make a copy of this annotation set in the test set project
    ann_set_test = PointAnnotationSet.objects.get_or_create(name=ann_set.name,
                                                                    owner=user,
                                                                    collection=subset_test,
                                                                    count=ann_set.count,
                                                                    methodology=ann_set.methodology)[0]
    ann_set_test.save()

    #TODO: Finish this so annotation points get moved across as well as just images
    annotations =
    images_test = subset_test.images

#
#TODO: This isn't quite right - it gets 15% of each campaign, not 15% of each dive...
#TODO: We moved the COLLECTION across for images, but not the point annotation sets. Need to do the same thing (make
# copies, delete old points, add new)
#
# for subset in Collection.objects.filter(parent__exact=proj):
#     print subset.name, subset.images.count()
#
# for subset_test in Collection.objects.filter(parent__exact=proj_test):
#     print subset_test.name, subset_test.images.count()
#     for ann_set in PointAnnotationSet.objects.filter