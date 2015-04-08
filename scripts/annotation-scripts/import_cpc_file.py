"""
Created on 25/09/2012


@author: mbew7729
"""
import os
import sys
from sklearn.cross_validation import train_test_split

sys.path.append('/home/auv/git/squidle-playground')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from django.conf import settings

from django.contrib.auth.models import User
from libxml2mod import name
import logging

import csv

import pandas as pd
import numpy as np

import annotations.models
from catamidb.models import Image
from collection.models import Collection
from collection.authorization import apply_collection_permissions

POINTINDEX = 'point_index'
CPCFOLDER = 'cpc_folder'
IMAGEFILENAME = 'image_name'
LABELNUMBER = 'label_number'
HFRAC = 'fraction_from_image_left'
VFRAC = 'fraction_from_image_top'
LABEL = 'cpc_label'
LABELGROUP = 'cpc_group'
NOTES = 'notes'
HEADERLINES = 6

RANDOM_METHODOLOGY = 0
logging.root.setLevel(logging.INFO)


class CPCMappingError(ValueError):
    pass


class ImagesNotInDatabaseError(Exception):
    """
    Raise when we expect an image to be in the database, but find it isn't.
    """
    pass


class DuplicateCPCError(ValueError):
    """
    When multiple cpc files referring to the same image are imported, this is probably an error.
    """
    pass


class CPCFolderParser:
    def __init__(self, folder_path, image_name_remapping_file=None):
        self.bigdf = self.parse_files(folder_path, image_name_remapping_file)
        self.image_name_remapping_file = image_name_remapping_file
        self.folder_path = folder_path

    @staticmethod
    def parse_files(folder_path, image_name_remapping_file):
        """
        Given all *.cpc files in the folder_path, return a concatenated data frame with each row as a labelled point:
        fraction_from_image_left: A float [0,1] with distance across the image from the left edge.
        fraction_from_image_right: A float [0,1] with distance down the image from the top edge.
        image_name: The filename (minus extension) of the image.
        label_number: The number of the labelled point within the image (unique per cpc file, typically ~1-50).
        cpc_label: The CPC label assigned to the point.
        :return:
        """
        df_list = []
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filter(lambda f: f[-4:].lower() == '.cpc', filenames):
                cp = CPCFileParser(os.path.join(dirpath, filename))
                df = cp.parse()
                df_list.append(df)
        if len(df_list) == 0:
            raise ValueError('No *.cpc files found in the folder provided.')
        bigdf = pd.concat(df_list, axis=0)
        logging.info('Found {} cpc points'.format(len(bigdf)))

        if image_name_remapping_file is not None:
            remap = pd.read_csv(image_name_remapping_file)
            bigdf = pd.merge(bigdf, remap, left_on='image_name', right_on='mod_image_name', how='left')
            if np.any(bigdf.auv_image_name.isnull()):
                logging.error(bigdf[bigdf.auv_image_name.isnull()])
                raise ValueError('Remap file does not contain all the images referenced by the CPC files!')
            else:
                bigdf.pop('image_name')
                bigdf.rename(columns={'auv_image_name': 'image_name'}, inplace=True)
        return bigdf

    def get_cpc_set(self):
        """
        Gets the set of cpc labels from the processed folder.
        :return: python set of cpc labels.
        """
        self.cpc_set = set(self.bigdf.cpc_code)
        return self.cpc_set

    def load_cpc2labelid(self, cpc2labelid_file):
        """
        Read cpc2caab_file and joins the appropriate caab_codes onto the data
        frame
        :param cpc2caab_file: a csv file with two columns: cpc_code and caab_code
        :return: cpc2caabs, a pandas Series of caab codes indexed by cpc_codes
        """
        cpc2labelids = pd.read_csv(cpc2labelid_file).fillna('')
        bigdf = pd.merge(self.bigdf, cpc2labelids, on='cpc_code', how='left')
        all_pts = len(bigdf)
        bigdf = bigdf[bigdf.label_id.astype(str) != 'DO_NOT_IMPORT']
        if len(bigdf) < all_pts:
            logging.warning(
                'Discarding {} points (tagged as "DO_NOT_IMPORT"). {} points remaining.'.format(all_pts - len(bigdf),
                                                                                                len(bigdf)))

        annotations_missing_label_ids = bigdf[bigdf.label_id.isnull()]
        if len(annotations_missing_label_ids) > 0:
            missing_cpc_codes = set(annotations_missing_label_ids.cpc_code.values)
            raise CPCMappingError(
                "No CPC map for {} points, with CPC codes: {}".format(len(annotations_missing_label_ids),
                                                                      missing_cpc_codes))
        else:
            self.bigdf = bigdf

    def load_image_pks_from_database(self):
        """
        Look up the images we're trying to import in the database. Check they are all unique (by name), and present,
        then link their primary keys from the database into self.bigdf.
        :return: The set of images found in the database (as a django QuerySet).
        """
        duplicates = self.bigdf[self.bigdf.duplicated(['image_name', 'label_number'])]
        if len(duplicates) > 0:
            logging.warn(duplicates)
            duplicates.to_csv('duplicates.csv')
            raise DuplicateCPCError(
                'Tried to import {} image points that have been labelled more than once'.format(len(duplicates)))

        image_list = list(set(self.bigdf.image_name))
        image_q = Image.objects.filter(image_name__in=list(image_list))
        logging.debug(image_q.query)
        db_image_list = list(image_q.values_list('pk', 'image_name'))
        if len(db_image_list) > 0:
            dbimages = pd.DataFrame(db_image_list, columns=['pk', 'image_name'])
        else:
            raise ValueError('No images found in database (looking for e.g. {})'.format(image_list[0]))
        n_im = len(dbimages)
        n_unique = len(set(dbimages.image_name))
        if n_im != n_unique:
            raise ValueError(
                "{} of the images have duplicates by name, so we can't rely on name as a primary key".format(
                    n_im - n_unique))

        bigdf = pd.merge(self.bigdf, dbimages, on='image_name', how='left')
        missing_images = bigdf[bigdf.pk.isnull()]
        if len(missing_images) > 0:
            logging.warning('The following images were not found in the database:')
            logging.warning(missing_images)
            missing_images.groupby('image_name').aggregate({'pk': lambda pk: pk.iloc[0]}).to_csv('missing_images.csv')
            raise ValueError("{} of the images were not found in the database. Have they been imported?".format(
                len(image_list) - n_im))
        self.bigdf = bigdf

        self.image_q = image_q
        return image_q

    def populate_database(self, user, project, subset_name='Imported CPC Data', subset_description='',
                          annotation_set_name='CPC Imports', methodology=RANDOM_METHODOLOGY):

        images = pd.DataFrame(list(self.image_q.values('id', 'image_name'))).set_index('id')

        # Automatically create a test project, and test subset that mirrors the main one, to move the test labels to.
        project_test = Collection.objects.get_or_create(
            name='AUSBEN2014_TEST',
            description='Australian benthic annotation test set',
            owner=user,
            creation_info="Imported CPC labels",
            is_locked=False
        )[0]
        project_test.save()
        apply_collection_permissions(user=user, collection=project_test)

        # The subset of the main project to put these labels (e.g. geographic region)
        subset = Collection.objects.get_or_create(
            name=subset_name,
            description=subset_description,
            owner=user,
            parent=proj,
            creation_info="Imported CPC labels",
            is_locked=False
        )[0]
        subset.save()

        # The equivalent subset, in the test project
        subset_test = Collection.objects.get_or_create(
            name=subset_name,
            description=subset_description,
            owner=user,
            parent=project_test,
            creation_info="Imported CPC labels",
            is_locked=False
        )[0]
        subset_test.save()

        subset.images.add(*images.index)
        apply_collection_permissions(user=user, collection=subset)
        apply_collection_permissions(user=user, collection=subset_test)

        img_counts = self.bigdf.image_name.value_counts()
        cpc_count_hist = img_counts.value_counts()
        if len(cpc_count_hist) > 1:
            cpc_count = cpc_count_hist.argmax()
            logging.warning('CPC files do not all have the same number of counts per image: {}'.format(cpc_count_hist))
            logging.warning('The following images did not have %d points labelled:' % cpc_count)
            logging.warning(img_counts[img_counts != cpc_count])
        else:
            cpc_count = cpc_count_hist.index[0]

        point_annotation_set = annotations.models.PointAnnotationSet.objects.get_or_create(name=annotation_set_name,
                                                                                           owner=user,
                                                                                           collection=subset,
                                                                                           count=cpc_count,
                                                                                           methodology=methodology)[0]
        point_annotation_set.save()
        point_annotation_set_test = \
            annotations.models.PointAnnotationSet.objects.get_or_create(name=annotation_set_name,
                                                                        owner=user,
                                                                        collection=subset_test,
                                                                        count=cpc_count,
                                                                        methodology=methodology)[0]

        point_annotation_set_test.save()

        im_bigdf = self.bigdf.set_index('pk')
        point_annotations = []
        bigdf_train = im_bigdf.loc[images.index]
        for idx, row in bigdf_train.iterrows():
            point_annotations.append(
                annotations.models.PointAnnotation(
                    annotation_set=point_annotation_set,
                    x=row.fraction_from_image_left,
                    y=row.fraction_from_image_top,
                    level=0,
                    image_id=idx,
                    label_id=row.label_id,
                    labeller=user
                )
            )
        existing_annotations = annotations.models.PointAnnotation.objects.filter(
            annotation_set__exact=point_annotation_set)
        print "already found %d annotations for training set. Will delete and reimport" % existing_annotations.count()
        existing_annotations.delete()
        annotations.models.PointAnnotation.objects.bulk_create(point_annotations)


class CPCFileParser:
    def __init__(self, filepath):
        """
    This class parses a CPCe file (*.cpc) into a more useful and manageable
    format than the original. All data should be retained, and the output
    can be saved to file.
    NB: IT ASSUMES THE CPC FILE REFERS ONLY TO A SINGLE IMAGE.

    filepath: (str) path to the .cpc file.
    """
        self.filepath = filepath
        self.folder, self.filename = os.path.split(filepath)
        self.parsed = None

    def parse(self):
        """
    Reads the .cpc file, returning a data frame of:
    image_name: The name of the colour image the labels in this file belong to
    label_number: The number (within this file) of the label (e.g. 1 to 50)
    cpc_code: The cpc label code (e.g. "ECK") for a given point.
    """
        r = csv.reader(open(self.filepath, 'r'))
        lines = [line for line in r]

        # Get the header data
        path_list = lines[0][1].split('\\')
        image_filename = os.path.splitext(path_list[-1])[0]  # With no extension

        hscale, vscale = (np.ceil(float(l)) for l in lines[2])

        # This may include things that aren't actually points, like rugosity, when cpc points are used as a proxy
        # for whole image tags. Filtering of those points is left to further down the chain.
        num_points = int(lines[HEADERLINES - 1][0])

        # Get the coordinates of the random points that were hand labelled.
        # These are listed first, for some reason, then labels are listed later.
        point_coords = np.array(lines[HEADERLINES:HEADERLINES + num_points], dtype=float)
        point_coords[:, 0] /= hscale
        point_coords[:, 1] /= vscale
        assert point_coords.min() >= 0
        assert point_coords.max() <= 1

        # Meta data is a list of label_number, label, "Notes", note_content
        metadata = np.array(lines[HEADERLINES + num_points:HEADERLINES + 2 * num_points])
        assert len(metadata) == len(point_coords)

        df = pd.DataFrame(point_coords, columns=[HFRAC, VFRAC])
        df['image_name'] = image_filename
        df['label_number'] = range(len(df))
        df['cpc_code'] = metadata[:, 1]
        self.parsed = df
        return df


if __name__ == '__main__':
    user = User.objects.get(id=61)
    proj = Collection.objects.get_or_create(
        name='AUSBEN2014_TRAIN',
        description='Australian benthic annotation training set',
        owner=user,
        creation_info="Imported CPC labels",
        is_locked=False
    )[0]
    proj.save()
    apply_collection_permissions(user=user, collection=proj)

    parser_list = []

    # For Tasmanian data, need to fudge it so we copy classes from an excel file, because UNIDxx was only identified as UNID in the original cpc files.
    cp = CPCFolderParser('real_cpc_data_to_import/public/Tasmania 2008')
    tas_classes = pd.read_csv('AUV_ScoredData_ByPoints_Long.csv')
    tas_classes['label_number'] = tas_classes.Point_No.apply(lambda s: s[2:]).astype(int)+4
    tas_classes['image_name'] = tas_classes.IMAGE_NAME_LEFT.apply(lambda s: os.path.splitext(s)[0])
    bigdf = pd.merge(cp.bigdf, tas_classes[['image_name', 'label_number', 'Species_Code']],
                     on=['image_name', 'label_number'], how='left')
    unid = bigdf.cpc_code == 'UNID'
    bigdf.loc[unid, 'cpc_code'] = bigdf.loc[unid, 'Species_Code'].fillna('UNID')
    bigdf.pop('Species_Code')

    cp.bigdf = bigdf
    cp.load_cpc2labelid('cpc2labelid_tas08.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/Tasmania 200903')
    tas_classes = pd.read_csv('AUV_ScoredData_ByPoints_Long.csv')
    tas_classes['label_number'] = tas_classes.Point_No.apply(lambda s: s[2:]).astype(int) + 4
    tas_classes['image_name'] = tas_classes.IMAGE_NAME_LEFT.apply(lambda s: os.path.splitext(s)[0])
    bigdf = pd.merge(cp.bigdf, tas_classes[['image_name', 'label_number', 'Species_Code']],
                     on=['image_name', 'label_number'], how='left')
    unid = bigdf.cpc_code == 'UNID'
    bigdf.loc[unid, 'cpc_code'] = bigdf.loc[unid, 'Species_Code'].fillna('UNID')
    bigdf.pop('Species_Code')

    cp.bigdf = bigdf
    cp.load_cpc2labelid('cpc2labelid_tas08.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/Tasmania 200906')
    tas_classes = pd.read_csv('AUV_ScoredData_ByPoints_Long.csv')
    tas_classes['label_number'] = tas_classes.Point_No.apply(lambda s: s[2:]).astype(int) + 4
    tas_classes['image_name'] = tas_classes.IMAGE_NAME_LEFT.apply(lambda s: os.path.splitext(s)[0])
    bigdf = pd.merge(cp.bigdf, tas_classes[['image_name', 'label_number', 'Species_Code']],
                     on=['image_name', 'label_number'], how='left')
    unid = bigdf.cpc_code == 'UNID'
    bigdf.loc[unid, 'cpc_code'] = bigdf.loc[unid, 'Species_Code'].fillna('UNID')
    bigdf.pop('Species_Code')

    cp.bigdf = bigdf
    cp.load_cpc2labelid('cpc2labelid_tas08.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/New South Wales 2010')
    cp.load_cpc2labelid('cpc2labelid_nsw.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/New South Wales 2012')
    cp.load_cpc2labelid('cpc2labelid_nsw.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/South East Queensland 2010',
                         'real_cpc_data_to_import/public/South East Queensland 2010/image_name_mapping.csv')
    cp.load_cpc2labelid('cpc2labelid_qld2010.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/Western Australia 2011')
    cp.load_cpc2labelid('cpc2labelid_wa.csv')
    parser_list.append(cp)

    cp = CPCFolderParser('real_cpc_data_to_import/public/Western Australia 2012')
    cp.load_cpc2labelid('cpc2labelid_wa.csv')
    parser_list.append(cp)
    #TODO: Seems to be a large bunch of images with e.g. 51 or 49 cpc points. Investigate.

    cp = CPCFolderParser('real_cpc_data_to_import/public/Western Australia 2013')
    cp.load_cpc2labelid('cpc2labelid_wa.csv')
    parser_list.append(cp)

    for cp in parser_list:
        print(cp.folder_path)
        print('Loaded cpc2labelid file')
        cp.load_image_pks_from_database()
        print('Found linked images in database.')
        campaign_name = os.path.split(cp.folder_path)[-1]
        cp.populate_database(user=user,
                             project=proj,
                             subset_name=campaign_name,
                             subset_description='',
                             annotation_set_name=campaign_name,
                             methodology=RANDOM_METHODOLOGY)
        print('Finished populating database')


        # Code to generate caab2labelid files. NB: BE CAREFUL RUNNING THIS, most of them require some manual editing
        # afterwards.
        # for g in ['nsw', 'qld2010', 'tas08', 'wa2011']:
        # g = 'tas08'
        # cpc2caab = pd.read_csv('cpc2caab_{}.csv'.format(g))
        # caab2labelid = pd.read_csv('caab2labelid.csv')
        # caab2labelid.caab_code = caab2labelid.caab_code.astype('str')
        # df = pd.merge(cpc2caab, caab2labelid, on='caab_code', how='left').set_index('cpc_code')
        # df.to_csv('cpc2labelid_{}.csv'.format(g), float_format='%.f')
        #
        # unmatched = df.loc[df.label_id.isnull()]
        # print(g)
        # print(unmatched)
        #
        # import annotations.models as m
        # new_caab = m.AnnotationCode(
        # id=658,
        # caab_code=10000917,
        # cpc_code='SPCC',
        # point_colour='FFFF33',
        # code_name="Sponges: Crusts: Creeping / ramose",
        # description="",
        # parent=m.AnnotationCode.objects.get(caab_code=10000901),
        # )