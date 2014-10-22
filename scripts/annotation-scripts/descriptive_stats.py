__author__ = 'mbewley'
import os
import sys

sys.path.append('/home/auv/git/squidle-playground')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from django.conf import settings

from collection.models import Collection
from annotations.models import PointAnnotationSet, PointAnnotation
from catamidb.models import Deployment, Image

dataset = Collection.objects.get(name__exact='AUSBEN2014')
print dataset

subsets = Collection.objects.filter(parent__exact=dataset)
ann_sets = PointAnnotationSet.objects.filter(collection__in=subsets)
print ann_sets

import pandas as pd


def points2df(points):
    df = pd.DataFrame(list(points.values('image__image_name', 'x', 'y', 'label', 'label__cpc_code',
                                         'image__pose__depth',
                                         'image__pose__date_time',
                                         'image__pose__position')))
    df.rename(columns={'image__image_name': 'image_name',
                       'label__cpc_code': 'code',
                       'image__pose__depth': 'depth',
                       'image__pose__date_time': 'date_time',
                       'image__pose__position': 'position'},
              inplace=True)
    return df


def df2label_counts(df):
    label_counts = df.groupby('code').count().iloc[:, 0].copy()
    label_counts.sort(ascending=False)
    return label_counts

for ann_set in ann_sets:
    pas = PointAnnotation.objects.filter(annotation_set__exact=ann_set)
    print '{} has {} points'.format(ann_set.name, pas.count())
    df_campaign = points2df(pas)
    label_counts_campaign = df2label_counts(df_campaign)
    image_counts_campaign = len(df_campaign.groupby('image_name'))
    print (label_counts_campaign / label_counts_campaign.sum()).head(10)
    print 'Number of images: {}'.format(image_counts_campaign)
    depth = df_campaign.depth
    print 'Depth (min, mean, max): [{}, {}, {}]'.format(depth.min(), depth.mean(), depth.max())

all_points = PointAnnotation.objects.filter(annotation_set__in=ann_sets)

print 'Total number of cpc points:', all_points.count()

all_df = points2df(all_points)

label_counts_all = df2label_counts(all_df)
label_counts_norm = label_counts_all / label_counts_all.sum()
print label_counts_norm.head(10)

image_counts_all = len(all_df.groupby('image_name'))
print 'Total number of images:', image_counts_all


# Get original deployments
deployments = Deployment.objects.filter(pose__image__image_name__in=list(set(all_df.image_name)))
full_image_set = Image.objects.filter(pose__deployment__in=deployments)
print 'Total number of images from all deployments with labelled images:', full_image_set.count()