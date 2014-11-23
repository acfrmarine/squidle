from django.contrib.gis.geos import GEOSGeometry
from os.path import join
import logging

__author__ = 'mbewley'
import os
import sys

import numpy as np

sys.path.append('/home/auv/git/squidle-playground')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from django.conf import settings

from collection.models import Collection
from annotations.models import PointAnnotationSet, PointAnnotation, AnnotationCode
from catamidb.models import Deployment, Image, Pose, ScientificPoseMeasurement

dataset = Collection.objects.get(name__exact='AUSBEN2014')
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


# all_df = points2df(all_points)
# all_df.to_csv('AUSBEN2014_all.csv')

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
    parent_id = node.sq.parent_id
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

import smartpy.featureextraction.patchtransforms as pt
from smartpy.metadata.general import DataManager

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
    colour_transform_func=pt.getGray,
    channels='all'
)

features = feature_extractor.calculate_features(all_points[:100])
features.to_csv('sample_features.csv')

# for node in aroot:
#     print node.sq.code_name
#     node.set_save_dir('.')
#
#     node.set_descriptor_extractor(feature_extractor=feature_extractor, method=method)
#     features =

# def extract_features(tree, method, feature_extractor, save_path, overwrite):
# """
#     extracts features for all nodes in the given tree.
#
#     :param tree: The root node of a ClassificationTreeNode tree.
#     :param method: The training method (e.g. 'local' or 'global')
#     :param savePath: The path to save the features to.
#     """
#     save_dir = join(DATADIR, save_path)
#
#     for node in tree:
#         if node.has_parent():
#             logging.info('Extracting features on %s' % node.node_name)
#             logging.info('radii=%s, points=%s, ps=%s' % (feature_extractor.radii,
#                                                          feature_extractor.points,
#                                                          feature_extractor.patch_size))
#             node.set_save_dir(save_dir)
#             node.set_descriptor_extractor(feature_extractor, method=method)
#             node.save_features(batchsize=100, overwrite=overwrite)
#             break
#
#
# methods = ['siblings',
#            'inclusive']
#
# p_r_lists = [
#     [[8, 16, 24], [1, 2, 3]],
# ]
# patch_sizes = [15, 31, 63, 95, 127]
#
# args = []
# for method in methods:
#     for patch_size in patch_sizes:
#         for points, radii in p_r_lists:
#             save_path = 'ftype-{0:s}_method-{1:s}_ps-{2:d}_lbptype-{3:s}_trans-{4:s}_points-{5:s}_radii-{6:s}'.format(
#                 'LBPSquare',
#                 method,
#                 patch_size,
#                 lbp_type,
#                 trans_func.func_name,
#                 points,
#                 radii,
#             )
#             feature_extractor = de.LBPSquarePatchExtractor(
#                 data_manager=dm,
#                 lbp_type=lbp_type,
#                 points=points,
#                 radii=radii,
#                 colour_transform_func=trans_func,
#                 patch_size=patch_size
#             )
#             args.append({'method': method,
#                          'feature_extractor': feature_extractor,
#                          'save_path': save_path,
#                          'patch_size': patch_size})
#
# # <markdowncell>
#
# # ## Extracting features
# # Warning: This process takes some time, and does not need to be run if features have already been extracted and saved as a file (using the above feature extractor object)
#
# # <codecell>
#
# OVERWRITE = False
#
# for i in range(len(args)):
#     a = args[i]
#     extract_features(tree=TREE,
#                      method=a['method'],
#                      feature_extractor=a['feature_extractor'],
#                      save_path=a['save_path'],
#                      overwrite=OVERWRITE)
#
# # <markdowncell>
#
# # # Classifier Training
# # With the large range of parameter combinations for feature extraction above, we use a simple classifier (Logistic Regression) to assess the best performing combinations. 'Auto' class weight is used to account for class imbalance in most of the classifiers.
# # Here, we choose to train on both inclusive and siblings data sets, as there was no clear winner in the FSR conference paper.
#
# # <markdowncell>
#
# # ## Defining the classifier
# # We perform a grid search over the fitting parameters, and use 'auto' class weighting to adjust for unbalanced classes.
#
# # <markdowncell>
#
# # ## Training the classifiers
# # This next block of code actually trains the classifiers.
#
# # <codecell>
#
# from sklearn.grid_search import GridSearchCV
# # from sklearn.svm import SVC
# from sklearn.linear_model import LogisticRegression
# import smartpy.classification.classifiers as classifiers
# import numpy as np
#
# NJOBS = 3
# PARAMSELECTFOLDS = 3
#
#
# def train_classifier(tree, method, save_path, feature_extractor):
#     """
#     Trains and saves classifier models for all nodes in the given tree.
#
#     :param tree: The root node of a ClassificationTreeNode tree.
#     :param method: The training method (e.g. 'local' or 'global')
#     :param savePath: The path to save the classifier models to.
#     """
#     save_dir = join(DATADIR, save_path)
#
#     tree.features_cache = None
#     for node in tree:
#         node.set_feature_file('node_PHYSICAL.features.tsv')  # The feature file is the same for all nodes...
#
#     for node in tree:
#         if node.has_parent():
#             node.set_save_dir(save_dir)
#             logging.debug('Setting descriptor extractor')
#             node.set_descriptor_extractor(feature_extractor, method=method, train=False)
#             try:
#                 # raise IOError # ARTIFICIALLY FORCE RETRAINING OF EVERYTHING
#                 node.load_classifier_model()
#             except IOError:
#                 logging.debug('Setting classifier model')
#                 clf = GridSearchCV(
#                     estimator=LogisticRegression(class_weight='auto'),
#                     param_grid={'C': 10 ** np.arange(0, 4)},
#                     scoring='f1',
#                     n_jobs=NJOBS,
#                     cv=PARAMSELECTFOLDS,
#                     verbose=0)
#                 # clf = LogisticRegression(C=64, class_weight='auto')
#                 classifierModel = classifiers.ClassifierModel(data_manager=dm,
#                                                               sklearn_classifier=clf)
#                 node.set_classifier_model(classifierModel)
#                 node.train_classifier(method, 'training')
#             finally:
#                 node.unload_classifier_model()
#                 logging.debug('Classifier unloaded')
#
# # <codecell>
#
# import time
#
# logging.root.setLevel(logging.ERROR)
#
# for i in range(len(args)):
#     a = args[i]
#     t1 = time.time()
#     train_classifier(tree=TREE,
#                      method=a['method'],
#                      feature_extractor=a['feature_extractor'],
#                      save_path=a['save_path'])
#     t2 = time.time()
#     tt = t2 - t1
#     args[i]['training_time'] = tt
#     print a['save_path'], 'Took %0.2fs to train all nodes' % tt
#
# # <markdowncell>
#
# # # Measuring Performance
# # After classifier training, it is important to evaluate the performance against a separate test set.
#
# # <codecell>
#
# combos = [
#     ['none', 'greedywalk', True, 'modified-hierarchical'],
#     ['none', 'greedywalk', False, 'modified-hierarchical'],
#     ['multiply', 'argmax', True, 'modified-hierarchical'],
#     ['multiply', 'argmax', False, 'modified-hierarchical'],
#     ['geometricmean', 'argmax', True, 'modified-hierarchical'],
#     ['geometricmean', 'argmax', False, 'modified-hierarchical'],
#     ['none', 'argmax', False, 'modified-hierarchical'],
# ]
#
# results = []
# logging.root.setLevel(logging.INFO)
# for i in range(len(args)):
#     a = args[i]
#     TREE.clear_feature_cache()
#     for node in TREE:
#         save_dir = join(DATADIR, a['save_path'])
#         node.set_feature_file('node_PHYSICAL.features.tsv')
#         if node.has_parent():
#             node.set_save_dir(save_dir)
#             node.set_descriptor_extractor(a['feature_extractor'])
#             node.load_classifier_model()
#     filename = join(os.getcwd(), a['save_path'])
#     logging.info("Saving performance for %s" % filename)
#
#     for pm, sm, mlnp, loss in combos:
#         logging.info('\n')
#         logging.info(
#             'Computing performance for {0:s}, {1:s}, mlnp={2:b}, losstype={3:s}'.format(
#                 pm, sm, mlnp, loss))
#         hf1 = TREE.calculate_performance(data_set_name='validation',
#                                          prob_aggregation_method=pm,
#                                          selection_method=sm,
#                                          mlnp=mlnp,
#                                          losstype=loss)
#         results.append([
#             a['method'],
#             a['patch_size'],
#             a['feature_extractor'],
#             a['training_time'],
#             pm, sm, mlnp, loss, hf1
#         ])
#
# # <codecell>
#
# import pandas as pd
#
# COLS = ['Method', 'Patch Size', 'Feature Extractor', 'Training Time',
#         'Prob Agg Method', 'Selection Method', 'MLNP', 'Loss Type', 'Hierarchical F1']
# df = pd.DataFrame(results, columns=COLS)
# df['LBP Points'] = df['Feature Extractor'].apply(lambda x: x.points)
# df['LBP Radii'] = df['Feature Extractor'].apply(lambda x: x.radii)
# df.sort(columns='Hierarchical F1', ascending=False, inplace=True)
# df.to_csv('performance_results.csv')
#
# # <codecell>
#
# print df[['Patch Size', 'LBP Points', 'LBP Radii', 'Method', 'Prob Agg Method', 'Selection Method',
#           'MLNP', 'Training Time', 'Hierarchical F1'
# ]].set_index('Hierarchical F1').head(20).to_latex(float_format=lambda f: '%0.2f' % f)
#
# # <markdowncell>
#
# # # Performance Plots
# # Below, we plot performance for different models, using different losses. These plots summarise the model selection process, and are intended to be used in the paper.
#
# # <codecell>
#
# import matplotlib as mpl
#
# df = pd.read_csv('performance_results.csv', index_col=0)
# minval = df['Hierarchical F1'].min()
# maxval = df['Hierarchical F1'].max()
# for gname, g in df.groupby(['Prob Agg Method', 'Selection Method', 'MLNP', 'Loss Type']):
#     figure(figsize=(14, 4.5))
#     i = 1
#
#     def fe2str(fe):
#         return str(fe).split('(')[1][18:-1]
#
#     for sibinc, g2 in g.groupby('Method'):
#         subplot(1, 2, i)
#         # TODO: Fix y index
#         lbp_params = list(set(df['Feature Extractor'].apply(lambda fe: fe2str(fe))))
#         lbp_params.sort()
#         ind_dic = {}
#         for j, lp in enumerate(lbp_params):
#             ind_dic[lp] = j
#         inds = range(len(lbp_params))
#         scatter(g2['Patch Size'], g2['Feature Extractor'].apply(lambda fe: ind_dic[fe2str(fe)]),
#                 c=g2['Hierarchical F1'],
#                 cmap=mpl.cm.hot_r, vmin=minval, vmax=maxval,
#                 s=150)
#         # for fe, g3 in g2.groupby('Feature Extractor'):
#         #             lbp_combo_name = fe2str(fe)
#         #             print g3
#         #             plot(g3['Patch Size'], g3['Hierarchical F1'], label=lbp_combo_name)
#         legend()
#         title(sibinc, size='x-large')
#         xlabel('Patch Size (px)')
#         ylabel('LBP Parameters ([points], [radii])')
#         colorbar()
#         yticks(ind_dic.values(), ind_dic.keys())
#         i += 1
#     figtext(0.5, 0.97, gname, ha='center')
#     tight_layout()
# df.sort('Hierarchical F1', ascending=False)
#
# # <markdowncell>
#
# # # Conclusions
# # We now use paired t-tests to form statistically sound conclusions of which model parameters are inherently superior. For each parameter (LBP parameters, patch size, prediction type, siblings/inclusive), we have paired tests (the same model trained with the parameter in each state), and values (f1-score). We can perform a two sided t-test on the difference in means of the f1-scores, to see if one setting of that parameter is superior to the other.
#
# # <codecell>
#
# # %load_ext rmagic
# cols = array(['Patch Size', 'LBP Radii', 'Method', 'Hierarchical F1'])
# df2 = df[cols]
# df2['Prediction'] = df['Prob Agg Method'] + df['Selection Method'].apply(lambda x: '_%s' % x) + df['MLNP'].apply(
#     lambda x: '_%s' % x)
# df2
#
# # <codecell>
#
# with open('performance_table.tex', 'w') as f:
#     f.write(df2.head(20).to_latex())
#
# # <markdowncell>
#
# # %%R -i df2
# # df2$Patch.Size <- as.factor(df2$Patch.Size)
# # fit <- aov(Hierarchical.F1 ~ Patch.Size + LBP.Radii + Method + Prediction, data=df2)
# # t <- TukeyHSD(fit, ordered=TRUE)
# # plot(t)
# # t
#
# # <codecell>
#
# filter(lambda s: s.endswith('tex'), os.listdir(os.getcwd()))
#
# # <codecell>
#
#
