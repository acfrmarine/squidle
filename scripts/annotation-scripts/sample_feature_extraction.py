from django.contrib.gis.geos import GEOSGeometry
from os.path import join
import logging
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LogisticRegression


__author__ = 'mbewley'
import os
import sys
import logging
# logging.root.setLevel(logging.DEBUG)
import numpy as np

sys.path.append('/home/auv/git/squidle-playground')
sys.path.append('/home/auv/git')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from smartpy.featureextraction import descriptors
from django.conf import settings

from collection.models import Collection
from annotations.models import PointAnnotationSet, PointAnnotation, AnnotationCode
from catamidb.models import Deployment, Image, Pose, ScientificPoseMeasurement

dataset = Collection.objects.get(name__exact='AUSBEN2014_TRAIN')
print dataset

subsets = Collection.objects.filter(parent__exact=dataset)
ann_sets = PointAnnotationSet.objects.filter(collection__in=subsets)
print ann_sets

import pandas as pd


def points2df(points):
    df = pd.DataFrame(list(points.values(
        'id', 'image__id', 'image__image_name', 'x', 'y', 'label', 'label__cpc_code',
        'image__pose__depth',
        'image__pose__date_time',
        'image__pose__position',
        'image__pose__deployment__short_name',
        'image__pose__deployment__campaign__short_name')))
    df.rename(columns={
        'id': 'kpid',
        'image__image_name': 'image_name',
        'label__cpc_code': 'code',
        'image__pose__depth': 'depth',
        'image__pose__date_time': 'date_time',
        'image__pose__position': 'position',
        'image__pose__deployment__short_name': 'deployment',
        'image__pose__deployment__campaign__short_name': 'campaign',
    },
              inplace=True)
    # Convert position to lat and lon
    positions = df.position.apply(lambda s: GEOSGeometry(s))
    df.pop('position')
    df['latitude'] = positions.apply(lambda p: p[1])
    df['longitude'] = positions.apply(lambda p: p[0])

    df.set_index('kpid', inplace=True)

    sm = ScientificPoseMeasurement.objects.all()
    df2 = pd.DataFrame(list(sm.values('pose__image__id', 'measurement_type__display_name', 'value')))
    df2.rename(columns={
        'pose__image__id': 'image__id',
        'measurement_type__display_name': 'measurement_type',
    },
               inplace=True)
    df2 = df2.pivot('image__id', 'measurement_type', 'value')
    df = df.join(df2, on='image__id')
    return df


def df2label_counts(df):
    label_counts = df.groupby('code').count().iloc[:, 0].copy()
    label_counts.sort(ascending=False)
    return label_counts


all_points = PointAnnotation.objects.filter(annotation_set__in=ann_sets)

print 'Total number of cpc points:', all_points.count()



# print(all_df.head(1).T)

squidle_codes = AnnotationCode.objects.all()

sys.path.append('/home/auv/git')
import smartpy.classification.hierarchical as h

node_dic = {}

# Create a dictionary of all the nodes, as classificationtreenode objects.
for sc in squidle_codes:
    node_dic[sc.id] = h.ClassificationTreeNode(squidle_code=sc)

# Go through the dictionary, setting parent and child nodes
for code_id, node in node_dic.items():
    parent_id = node.parent_id
    if parent_id is not None:
        parent = node_dic[parent_id]
        node.parent_node = parent
        parent.child_nodes.append(node)

# Get the root node, and check it's of the largest tree (catami):
biggest_root = None
tmp = 0
for code_id, node in node_dic.items():
    aroot = node.get_rootnode()
    aroot_n = len([n for n in aroot])
    if aroot_n > tmp:
        biggest_root = aroot
        tmp = aroot_n

# Remove root level unknown/noisy data that the human couldn't classify.
aroot.prune_node(273)
aroot.prune_node(274)
aroot.prune_node(655)

logging.root.setLevel(logging.DEBUG)
from sklearn.externals import joblib
joblib.dump(aroot, 'tree.pkl')
aroot.calculate_node_point_counts(all_points)

# Prune any nodes not found at all in the data set.
aroot.prune()
aroot.pretty_print_tree()
print 'Dumped tree to disk'

with open('catami.json', 'wb') as f:
    f.writelines(aroot.json_dump_tree())
print 'Wrote tree json to disk'

KPFILENAME = 'kpdata.csv'
KPCOORDFILENAME = 'kpcoords.csv'
DATASETFILENAME = 'dataset.csv'
MINIDATASETFILENAME = 'minidataset.csv'
DATADIR = '/home/mbewley/Development/ACFR/Data/Hierarchical'
IMAGEDIR = 'images'

import smartpy.featureextraction.descriptors as de

feature_extractor = de.LBPSquarePatchExtractor(
    patch_size=127,
    points=(8, 16, 24),
    radii=(1, 2, 3),
    lbp_type='uniform',
    colour_transform_func=lambda im: im.mean(axis=2).reshape(im.shape[0], im.shape[1]),
    channels='rgb'
)


features = feature_extractor.calculate_features(all_points)
features.to_csv('features.csv')
