import re

__author__ = 'mbewley'

'''
Retrospectively import the roll, pitch, yaw, temperature, salinity and depth data from netcdf files.
'''
import os
import sys

sys.path.append('/home/auv/git/squidle-playground')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catamiPortal.settings")

from django.conf import settings

import logging
import pandas as pd
import catamidb.models as cdb_models

from staging.auvimport import NetCDFParser, TrackParser


temperature = cdb_models.ScientificMeasurementType.objects.get(normalised_name='temperature')
salinity = cdb_models.ScientificMeasurementType.objects.get(normalised_name='salinity')
meas_types = [temperature, salinity]

RELEASE = '/media/water/RELEASE_DATA/'
'r20101021_035013_hendersonSth_04_broad'


def merge_poses_with_measurements(pose_df, meas_df):
    """
    Merge the pose and measurement dataframes, interpolating the measurements to match up with the pose
    times.
    :param pose_df:
    :param meas_df:
    :return:
    """
    # Interpolate the readings to get the reading equivalent at the same time as each pose is recorded.
    if len(meas_df) > 0:
        meas_df.drop_duplicates(inplace=True)
        meas_df_interp = meas_df.reindex(pose_df.index.union(meas_df.index)).interpolate()
        merge_df = pose_df.join(meas_df_interp)
        return merge_df
    else:
        return meas_df


def populate_scientific_measurements(campaign_name, deployment_startswith, meas_type):
    deployments = cdb_models.Deployment.objects.filter(short_name__startswith=deployment_startswith,
                                                       campaign__short_name__exact=campaign_name)
    # for d in deployments:
    #     print cdb_models.Campaign.objects.get(deployment__exact=d), d
    # raw_input('About to import %s measurements for %d dives - last chance to abort!' % (meas_type.normalised_name,
    #                                                                                     deployments.count()))
    p_ct = re.compile('ct.*\.csv$')
    for deployment in deployments:
        poses = cdb_models.Pose.objects.filter(deployment__exact=deployment)
        existing_measurements = cdb_models.ScientificPoseMeasurement.objects.filter(pose__in=poses,
                                                                                    measurement_type__exact=meas_type)
        if existing_measurements.count() > 0:
            logging.debug('Found %d measurements already in deployment %s' % (existing_measurements.count(), deployment))

            poses = poses.exclude(scientificposemeasurement__in=existing_measurements)
            if poses.count() == 0:
                logging.debug('Skipping %s, as measurements are present for all poses' % deployment.short_name)
                continue
            else:
                logging.info('Continuing, inserting extra measurements on %d poses' % poses.count())

        df = pd.DataFrame(list(poses.values(
            'id',
            'deployment_id__short_name',
            'image__web_location',
            'date_time'
        )))
        df.set_index('date_time', inplace=True)
        web_loc = df.image__web_location.ix[0]
        df.pop('image__web_location')
        path_base = os.path.join(RELEASE, os.path.join(*web_loc.split('/')[:2]))

        if not os.path.isdir(path_base):
            logging.warning('Skipping %s, as release folder not found (%s)' % (deployment.short_name, path_base))
            continue

        measurements = []
        readings = []

        path = os.path.join(RELEASE, path_base, 'hydro_netcdf')
        if os.path.isdir(path):
            netcdf_files = filter(lambda s: re.search('IMOS_AUV_ST.*\.nc', s), os.listdir(path))
            for nc in netcdf_files:
                with open(os.path.join(path, nc), 'r') as f:
                    netcdf = NetCDFParser(f)
                while True:
                    try:
                        readings.append(netcdf.next())
                    except IndexError:
                        break
            meas_df = pd.DataFrame(readings)
            if len(readings) > 0:
                meas_df.set_index('date_time', inplace=True)
        else:
            import datetime

            hydro_dirs = filter(lambda s: s.startswith('hydro'), os.listdir(path_base))
            if len(hydro_dirs) == 0:
                logging.warning('Skipping %s, as no folder of sensor data could be found' % deployment.short_name)
                continue
            path = os.path.join(RELEASE, path_base, hydro_dirs[0])
            files = filter(lambda s: p_ct.match(s), os.listdir(path))
            if len(hydro_dirs) == 1 & len(files) == 1 & os.path.isfile(os.path.join(path, files[0])):
                oldmeas_df = pd.read_csv(os.path.join(path, files[0]))
                for idx, row in oldmeas_df.iterrows():
                    oldmeas_df.loc[idx, 'date_time'] = datetime.datetime(
                        year=int(row.year), month=int(row.month), day=int(row.day), hour=int(row.hour),
                        minute=int(row.minute), second=int(row.second),
                        microsecond=int(1E6 * (row.second - int(row.second))))
                oldmeas_df.rename(columns={'sal': 'salinity', 'temp': 'temperature'}, inplace=True)
                meas_df = oldmeas_df[['date_time', 'salinity', 'temperature']]
                meas_df = meas_df.set_index('date_time').tz_localize('UTC')
            else:
                logging.warning('Skipping %s, as no sensor data files could be found' % deployment.short_name)
                logging.warning(hydro_dirs)
                logging.warning(files)
                logging.warning(os.path.join(path, files[0]))
                continue

        # Merge measurement df with poses, and make and bulk create models.
        merge_df = merge_poses_with_measurements(pose_df=df, meas_df=meas_df)
        for datetime, row in merge_df.iterrows():
            pose = cdb_models.Pose.objects.get(id__exact=row.id)
            m = cdb_models.ScientificPoseMeasurement(value=row[meas_type.normalised_name],
                                                     measurement_type=meas_type,
                                                     pose=pose)
            measurements.append(m)
        cdb_models.ScientificPoseMeasurement.objects.bulk_create(measurements)


logging.root.setLevel(logging.INFO)
for campaign in ['Tasmania 2008', 'Tasmania 200903', 'Tasmania 200906', 
                 'New South Wales 2010', 'New South Wales 2012',
                 'South East Queensland 2010',
                 'Western Australia 2011', 'Western Australia 2012', 'Western Australia 2013']:
    logging.info(campaign)
    for meas_type in [temperature, salinity]:
        logging.info(meas_type)
        populate_scientific_measurements(campaign_name=campaign,
                                         deployment_startswith='r20',
                                         meas_type=meas_type)
