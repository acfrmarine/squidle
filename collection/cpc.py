__author__ = 'mbewley'
"""
Created on 25/09/2012


@author: mbew7729
"""
import os
import csv

import pandas as pd
import numpy as np

from catamidb.models import Image

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


class CPCMappingException(ValueError):
    pass


class CPCFolderParser:
    def __init__(self, folder_path):
        self.bigdf, self.image_list, self.cpc_list = self.parse_files(folder_path)


    @staticmethod
    def parse_files(folder_path):
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
        bigdf = pd.concat(df_list, axis=0)
        temp = bigdf.set_index(['image_name', 'label_number']).sortlevel()
        assert temp.index.is_unique  # Is each image in the imported set only labelled once?
        image_list = temp.index.levels[0].values
        cpc_list = list(set(bigdf.cpc_code))
        return bigdf, image_list, cpc_list

    def load_cpc2labelid(self, cpc2labelid_file):
        """
        Read cpc2labelid_file and joins the appropriate caab_codes onto the data
        frame
        :param cpc2labelid_file: a csv file with two columns: cpc_code and caab_code
        :return: cpc2caabs, a pandas Series of caab codes indexed by cpc_codes
        """
        cpc2labelids = pd.read_csv(cpc2labelid_file)

        self.bigdf = pd.merge(self.bigdf, cpc2labelids, on='cpc_code', how='left')
        unassigned = set(self.bigdf.cpc_code[self.bigdf.caab_code.isnull()])
        if len(unassigned) > 0:
            raise CPCMappingException("Didn't find code mappings for: %s" % unassigned)

    def load_image_pks_from_database(self):
        """
        Look up the images we're trying to import in the database. Check they are all unique (by name), and present,
        then link their primary keys from the database into self.bigdf.
        :return: The set of images found in the database (as a django QuerySet).
        """


        image_q = Image.objects.filter(image_name__in=list(image_list))
        dbimages = pd.DataFrame(list(image_q.values_list('pk', 'image_name')), columns=['pk', 'image_name'])
        assert len(dbimages) == len(set(dbimages.image_name))  # Is each of the images from the database unique?
        assert len(dbimages) == len(image_list)  # Did we get a dbimage for every image we're trying to import?
        self.bigdf = pd.merge(self.bigdf, dbimages, on='image_name')
        return image_q


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
    cp = CPCFolderParser('example_cpc')
    cp.load_cpc2labelid('cpc2caab_wa2011.csv')
    cp.load_image_pks_from_database()
