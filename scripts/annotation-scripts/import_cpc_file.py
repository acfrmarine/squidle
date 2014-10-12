"""
Created on 25/09/2012


@author: mbew7729
"""
from libxml2mod import name
import logging
import os
import csv

import pandas as pd
import numpy as np

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")
from django.conf import settings
import annotations.models
from catamidb.models import Image
from collection.models import Collection

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
logging.root.setLevel(logging.DEBUG)


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
        cpc2labelids = cpc2labelids[cpc2labelids.label_id != 'DO_NOT_IMPORT']
        bigdf = pd.merge(self.bigdf, cpc2labelids, on='cpc_code', how='left')
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
            logging.warn('The following images were not found in the database:')
            logging.warn(missing_images)
            missing_images.groupby('image_name').aggregate({'pk': lambda pk: pk.iloc[0]}).to_csv('missing_images.csv')
            raise ValueError("{} of the images were not found in the database. Have they been imported?".format(
                len(image_list) - n_im))
        self.bigdf = bigdf

        self.image_q = image_q
        return image_q

    def populate_database(self, user_id, project_id, subset_name='Imported CPC Data', subset_description='',
                          annotation_set_name='CPC Imports', methodology=RANDOM_METHODOLOGY):
        subset = Collection(
            name=subset_name,
            description=subset_description,
            owner_id=user_id,
            is_locked=False,
            parent_id=project_id,
            creation_info="CPC labels apply to {} images".format(self.image_q.count())
        )
        subset.save()
        subset.images.add(*list(self.image_q))

        cpc_counts_per_image = self.bigdf.groupby('image_name').label_number.count()
        cpc_counts = set(cpc_counts_per_image.values)
        if len(cpc_counts) > 1:
            cpc_count = cpc_counts.median()
            logging.warn('CPC files do not all have the same number of counts per image')
            raise Exception('Images have a varying number of annotations, including: {}'.format(cpc_counts))
        else:
            cpc_count = list(cpc_counts)[0]

        point_annotation_set = annotations.models.PointAnnotationSet(name=annotation_set_name,
                                                                     owner_id=user_id,
                                                                     collection=subset,
                                                                     count=cpc_count,
                                                                     methodology=methodology)
        point_annotation_set.save()

        point_annotations = []
        # TODO: Confirm x and y are the correct way around.
        for i in range(len(self.bigdf)):
            point_annotations.append(
                annotations.models.PointAnnotation(
                    annotation_set=point_annotation_set,
                    x=self.bigdf.fraction_from_image_left.iloc[i],
                    y=self.bigdf.fraction_from_image_top.iloc[i],
                    level=0,
                    image_id=self.bigdf.pk.iloc[i],
                    label_id=self.bigdf.label_id.iloc[i],
                    labeller_id=user_id
                )
            )
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
    cp = CPCFolderParser('real_cpc_data_to_import/CPCe Files_For MichaelBewley')
    cp.load_cpc2labelid('cpc2labelid_wa.csv')

    # cp = CPCFolderParser('real_cpc_data_to_import/Tas08')
    # cp.load_cpc2labelid('cpc2labelid_tas08.csv')

    # cp = CPCFolderParser('real_cpc_data_to_import/SEQld_2010', 'real_cpc_data_to_import/SEQld_2010/image_name_mapping.csv')
    # cp.load_cpc2labelid('cpc2labelid_qld2010.csv')

    # cp = CPCFolderParser('real_cpc_data_to_import/NSW_2010-2012')
    # cp.load_cpc2labelid('cpc2labelid_nsw.csv')

    print('Loaded cpc2labelid file')
    cp.load_image_pks_from_database()
    print('Found linked images in database.')
    cp.populate_database(user_id=61,
                         project_id=1137,
                         subset_name='cpc import test #1',
                         subset_description='',
                         annotation_set_name='CPC Imports',
                         methodology=RANDOM_METHODOLOGY)
    print('Finished populating database')
    # Add code to authorise appropriate user on project and subset


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
    # caab_code=10000917,
    # cpc_code='SPCC',
    #     point_colour='FFFF33',
    #     code_name="Sponges: Crusts: Creeping / ramose",
    #     description="",
    #     parent=m.AnnotationCode.objects.get(caab_code=10000901),
    # )