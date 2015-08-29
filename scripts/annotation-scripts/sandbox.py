from django.contrib.gis.geos import GEOSGeometry
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
from smartpy.classification import classifiers
from smartpy.featureextraction import descriptors

from collection.models import Collection
from annotations.models import PointAnnotationSet, PointAnnotation, AnnotationCode

dataset = Collection.objects.get(name__exact='AUSBEN2014')
print dataset

subsets = Collection.objects.filter(parent__exact=dataset)
ann_sets = PointAnnotationSet.objects.filter(collection__in=subsets)
print ann_sets

import pandas as pd


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
aroot.pretty_print_tree()
aroot

from sklearn.externals import joblib
print 'Dumping tree to disk'
joblib.dump(aroot, 'tree.pkl')