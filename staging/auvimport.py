"""@brief Contains Utilities to help parse AUV files.
"""

# date handling
import datetime
from dateutil.tz import tzutc

# needed for thumbnailing
import Image
from cStringIO import StringIO

import glob
import os.path

# for netcdf files
from scipy.io import netcdf

from catamidb.models import ScientificMeasurementType, ScientificPoseMeasurement, Camera, Pose, Image
from .deploymentimport import image_import, LimitTracker

# for trackfiles from the data fabric
import csv

import logging
from django.db import transaction

logger = logging.getLogger(__name__)


class NetCDFParser:
    """A class to wrap retrieving values from AUV NetCDF files.

    The class requires a string with {date_string} in the place for the
    date string as it is not absolutely defined given the starting point.
    It searches for times within 10 seconds of the initial guess.

    It implements the iterator interface returning dictionaries with salinity,
    temperature and time of measurement.
    """
    secs_in_day = 24.0 * 3600.0
    imos_seconds_offset = 631152000.0
    imos_days_offset = imos_seconds_offset / secs_in_day

    def __init__(self, file_handle):
        self.file_handle = file_handle

        # the netcdf file
        self.reader = netcdf.netcdf_file(self.file_handle, mode='r')

        if not 'TIME' in self.reader.variables:
            # error, something is missing
            logger.warning("'TIME' not in netcdf file variables list.")
            raise KeyError("Key 'TIME' not in netcdf file variables list.")

        if not 'PSAL' in self.reader.variables:
            logger.warning("'PSAL' not in netcdf file variables list.")
            raise KeyError("Key 'PSAL' not in netcdf file variables list.")

        if not 'TEMP' in self.reader.variables:
            logger.warning("'TEMP' not in netcdf file variables list.")
            raise KeyError("Key 'TEMP' not in netcdf file variables list.")

        # the index we are up to...
        self.index = 0
        self.items = len(self.reader.variables['TIME'].data)
        logger.debug("Finished opening NetCDF file.")

    def imos_to_unix(self, imos_time):
        """Convert IMOS time to UNIX time.

        IMOS time is days since IMOS epoch which is 1950-01-01.
        """
        return (imos_time - self.imos_days_offset) * self.secs_in_day

    def unix_to_datetime(self, unix_time):
        """Short hand to convert unix to datetime."""
        return datetime.datetime.fromtimestamp(unix_time, tz=tzutc())

    def imos_to_datetime(self, imos_time):
        """Convert IMOS time to python datetime object.

        Utility function that chains the imos to unix and
        unix to datetime functions.
        """
        return datetime.datetime.fromtimestamp(self.imos_to_unix(imos_time),
                                               tz=tzutc())

    def next(self):
        """Get the next row in the NetCDF File.
        """
        i = self.index
        self.index += 1

        time = self.reader.variables['TIME'].data[i]
        sal = self.reader.variables['PSAL'].data[i]
        temp = self.reader.variables['TEMP'].data[i]

        return {'date_time': self.imos_to_datetime(time),
                'salinity': sal,
                'temperature': temp}


class TrackParser:
    """A class to parse the csv stereo pose tracks for AUV deployments.

    It can be given a URI that it will retrieve the file from. It returns
    a dictionary using the header row to determine the keys and the values
    for each row.
    """

    def __init__(self, file_handle):
        """Open a parser for AUV track files.

        -- file_location can be url or local file location.
        """
        self.file_handle = file_handle

        self.reader = csv.reader(self.file_handle)

        # skip until year is the first entry
        for row in self.reader:
            if len(row) >= 1 and row[0] == 'year':
                self.header = row
                break
                # the next line is the first data line
                # so construction is finished

    def next(self):
        """Get next row of track file."""
        # create a dict of the column headers and the values
        return dict(zip(self.header, self.reader.next()))

    def __iter__(self):
        return self


class AUVImporter(object):
    """Group of methods related to importing AUV missions.

    Methods to check for existence of required files etc.
    And a method to actually import the required files."""

    @classmethod
    def dependency_check(cls, deployment_path):
        # try and get files required, if throw exception
        # then return False (don't have required files)
        # else return True (do have what is required to import)
        try:
            files = cls.dependency_get(deployment_path)
        except IOError as e:
            return False
        else:
            return True

    @classmethod
    def dependency_get(cls, deployment_path):
        # find the hydro netcdf file
        netcdf_pattern = os.path.join(deployment_path,
                                      'hydro_netcdf/IMOS_AUV_ST_*Z_SIRIUS_FV00.nc')

        matches = glob.glob(netcdf_pattern)

        if len(matches) < 1:
            raise IOError("Cannot find netcdf file.")
        elif len(matches) > 1:
            raise IOError("Too many potential netcdf files.")

        logger.debug("NetCDF File: {0}".format(matches[0]))

        netcdf_filename = matches[0]

        # find the track file
        track_pattern = os.path.join(deployment_path,
                                     'track_files/*_latlong.csv')

        matches = glob.glob(track_pattern)

        if len(matches) < 1:
            logger.warning("Cannot file track file.")
            raise IOError("Cannot find track file.")
        elif len(matches) > 1:
            logger.warning("Too many potential track files.")
            raise IOError("Too many potential track files.")

        logger.debug("Track File: {0}".format(matches[0]))

        track_filename = matches[0]

        # get the image subfolder name
        image_folder_pattern = os.path.join(deployment_path, 'i*_gtif')

        matches = glob.glob(image_folder_pattern)

        if len(matches) < 1:
            raise IOError("Cannot find geotiff folder.")
        elif len(matches) > 1:
            raise IOError("Too many potential geotiff folders.")

        logger.debug("Images Folder: {0}".format(matches[0]))

        image_foldername = matches[0]

        files = {}
        files['netcdf'] = netcdf_filename
        files['track'] = track_filename
        files['image'] = image_foldername

        return files

    @classmethod
    def import_path(cls, auvdeployment, deployment_path):
        print "Importing auv path"
        files = cls.dependency_get(deployment_path)
        # do it this way as it was the way it was written...
        auvdeployment_import(auvdeployment, files)


@transaction.commit_on_success
def auvdeployment_import(auvdeployment, files):
    """Import an AUV deployment from disk.

    This uses the track file and hydro netcdf files (as per RELEASE_DATA).
    If the deployment comes in the CATAMI deployment format use that importer
    instead.

    Certain parameters of the deployment should be prefilled - namely short_name,
    campaign, license, descriptive_keywords and owner. The rest are obtained from the
    on disk information.

    Information obtained within the function includes start and end time stamps,
    start and end positions, min and max depths and mission aim. Additionally the
    region column, and other AUV specific fields are filled.
    """

    print "Entered!"
    logger.debug("Entering auvdeployment import")

    netcdf = NetCDFParser(open(files['netcdf'], "r"))
    track_parser = TrackParser(open(files['track'], "r"))
    image_subfolder = files['image']

    # now start going through and creating the data
    auvdeployment.mission_aim = "Generic Description."
    auvdeployment.min_depth = 14000
    auvdeployment.max_depth = 0

    auvdeployment.start_position = "POINT(0.0 0.0)"
    auvdeployment.end_position = "POINT(0.0 0.0)"
    auvdeployment.start_time_stamp = datetime.datetime.now()
    auvdeployment.end_time_stamp = datetime.datetime.now()

    auvdeployment.transect_shape = "POLYGON((0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0))"

    # we have to save the deployment so that everything else can link to it
    logger.debug("Initial save of auvdeployment.")
    auvdeployment.save()

    # create the left-colour camera object
    # we don't normally give out the right mono
    # images...
    leftcamera = Camera()

    leftcamera.deployment = auvdeployment
    leftcamera.name = "Left Colour"
    leftcamera.angle = Camera.DOWN_ANGLE

    leftcamera.save()

    # get the sm types that we are going to use
    logger.debug("Get handle on required ScientificMeasurementTypes")
    temperature = ScientificMeasurementType.objects.get(
        normalised_name='temperature')
    salinity = ScientificMeasurementType.objects.get(
        normalised_name='salinity')
    pitch = ScientificMeasurementType.objects.get(normalised_name='pitch')
    roll = ScientificMeasurementType.objects.get(normalised_name='roll')
    yaw = ScientificMeasurementType.objects.get(normalised_name='yaw')
    altitude = ScientificMeasurementType.objects.get(
        normalised_name='altitude')
    logger.debug("Got all required ScientificMeasurementTypes")

    first_pose = None
    last_pose = None

    lat_lim = LimitTracker('latitude')
    lon_lim = LimitTracker('longitude')

    logger.debug("First readings from netcdf file.")
    earlier_seabird = netcdf.next()
    later_seabird = netcdf.next()

    # now we get to the images... (and related data)
    logger.debug("Begin parsing images.")
    for row in track_parser:

        pose = Pose()
        image_name = os.path.splitext(row['leftimage'])[0] + ".tif"

        pose.deployment = auvdeployment

        pose_datetime = datetime.datetime.strptime(
            os.path.splitext(image_name)[0], "PR_%Y%m%d_%H%M%S_%f_LC16")
        pose.date_time = pose_datetime.replace(tzinfo=tzutc())
        pose.position = "POINT ({0} {1})".format(row['longitude'],
                                                 row['latitude'])

        pose.depth = float(row['depth'])

        # save now as it is complete and so image
        # can refer to it
        pose.save()

        # quickly calculate limit info

        if pose.depth > auvdeployment.max_depth:
            auvdeployment.max_depth = pose.depth

        if pose.depth < auvdeployment.min_depth:
            auvdeployment.min_depth = pose.depth

        lat_lim.check(row)
        lon_lim.check(row)

        # calculate image locations and create thumbnail
        campaign_name = auvdeployment.campaign.short_name
        deployment_name = auvdeployment.short_name
        image_path = os.path.join(image_subfolder, image_name)

        archive_path, webimage_path = image_import(campaign_name,
                                                   deployment_name, image_name,
                                                   image_path)

        image = Image()

        image.camera = leftcamera
        image.pose = pose
        image.archive_location = archive_path
        image.web_location = webimage_path

        image.save()

        # get the extra measurements from the seabird data
        while pose.date_time > later_seabird['date_time']:
            later_seabird, earlier_seabird = earlier_seabird, netcdf.next()

        # find which is closer - could use interpolation instead
        if (later_seabird['date_time'] - pose.date_time) > (
            pose.date_time - earlier_seabird['date_time']):
            closer_seabird = earlier_seabird
        else:
            closer_seabird = later_seabird

        # add those extra scientific measurements
        temp_m = ScientificPoseMeasurement()
        temp_m.measurement_type = temperature
        temp_m.value = closer_seabird['temperature']
        temp_m.pose = pose
        temp_m.save()

        sal_m = ScientificPoseMeasurement()
        sal_m.measurement_type = salinity
        sal_m.value = closer_seabird['salinity']
        sal_m.pose = pose
        sal_m.save()

        roll_m = ScientificPoseMeasurement()
        roll_m.measurement_type = roll
        roll_m.value = row['roll']
        roll_m.pose = pose
        roll_m.save()

        pitch_m = ScientificPoseMeasurement()
        pitch_m.measurement_type = pitch
        pitch_m.value = row['pitch']
        pitch_m.pose = pose
        pitch_m.save()

        yaw_m = ScientificPoseMeasurement()
        yaw_m.measurement_type = yaw
        yaw_m.value = row['heading']
        yaw_m.pose = pose
        yaw_m.save()

        alt_m = ScientificPoseMeasurement()
        alt_m.measurement_type = altitude
        alt_m.value = row['altitude']
        alt_m.pose = pose
        alt_m.save()

        # we need first and last to get start/end points and times
        last_pose = pose
        if first_pose is None:
            first_pose = pose

    auvdeployment.start_time_stamp = first_pose.date_time
    auvdeployment.end_time_stamp = last_pose.date_time

    auvdeployment.start_position = first_pose.position
    auvdeployment.end_position = last_pose.position

    auvdeployment.transect_shape = "POLYGON(({0} {2}, {0} {3}, {1} {3}, {1} {2}, {0} {2} ))".format(
        lon_lim.minimum,
        lon_lim.maximum,
        lat_lim.minimum,
        lat_lim.maximum)

    # now save the actual min/max depth as well as start/end times and
    # start position and end position
    auvdeployment.save()

    return auvdeployment
