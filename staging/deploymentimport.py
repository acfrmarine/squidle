"""Functions and classes for import of deployments matching the template."""

__author__ = "Lachlan Toohey"

import os
import os.path
import shutil
from django.db import transaction

import csv

import cv2
import datetime
from dateutil.parser import parse as dateparse
from dateutil.tz import tzutc

import catamidb.models as models

import logging

import staging.settings as staging_settings

logger = logging.getLogger(__name__)


class LimitTracker:
    """A class to easily track limits of a value/field.

    The field specifies the option key of the object to look up, or if
    field is None (the default) use the value itself. All values are
    converted to floats before comparison.

    minimum and maximum specify starting points.
    """

    def __init__(self, field=None, minimum=float("inf"),
                 maximum=float("-inf")):
        self.maximum = maximum
        self.minimum = minimum
        self.field = field

    def check(self, newobject):
        """Check a new value against the existing limits.
        """
        # check if field exists
        if self.field and self.field in newobject:
            value = float(newobject[self.field])
            # then see if it is a new maximum
            self.maximum = max(self.maximum, value)
            self.minimum = min(self.minimum, value)
        elif not self.field:
            value = float(newobject)
            self.maximum = max(self.maximum, value)
            self.minimum = min(self.minimum, value)


class CameraSensor(object):
    def __init__(self, camera, sensor_type, column_name):
        self.camera = camera
        self.sensor_type = sensor_type
        self.column_name = column_name.strip().lower()

    def apply_measurement(self, column_time, image, columns):
        # get all the times we need...
        actual_time = image.pose.date_time

        assert column_time == actual_time, "Image measurement and capture time do not match."

        assert image.camera == self.camera, "Image is from a different camera."

        # now get values for interpolation
        column_value = float(columns[self.column_name])

        im = models.ScientificImageMeasurement()
        im.image = image
        im.value = column_value
        im.measurement_type = self.sensor_type

        im.save()


class PoseSensor(object):
    def __init__(self, sensor_type, column_name):
        self.sensor_type = sensor_type
        self.column_name = column_name.strip().lower()

    def apply_measurement(self, pose, start_time, before_columns, end_time, after_columns):
        # get all the times we need...
        actual_time = pose.date_time


        # and now the time differences (a time delta - any units)
        dt = (end_time - start_time).total_seconds()
        dt_start = (actual_time - start_time).total_seconds()
        dt_end = (end_time - actual_time).total_seconds()

        # when we jump to the endtime everything goes crazy... so detect that here
        if end_time >= datetime.datetime(datetime.MAXYEAR-1, 1, 1, tzinfo=tzutc()):
            dt = 1.0
            dt_start = 0.0
            dt_end = 1.0

            start_value = float(before_columns[self.column_name])
            end_value = start_value
        else:
            start_value = float(before_columns[self.column_name])
            end_value = float(after_columns[self.column_name])

        # a few checks - could potentially remove later
        # as these may happen if people are naughty...
        # and need better checks etc.
        assert dt > 0.0, "Need positive time between rows."
        assert dt_start >= 0.0, "Start time after target interpolation time."
        assert dt_end > 0.0, "End time before target interpolation time."

        interpolated_value = (dt_end * start_value + dt_start * end_value) / dt

        pm = models.ScientificPoseMeasurement()
        pm.pose = pose
        pm.value = interpolated_value
        pm.measurement_type = self.sensor_type

        pm.save()


class Camera(object):
    def __init__(self, camera_name, angle, column_name, deployment, folder):
        self.camera_name = camera_name
        self.angle = angle
        self.column = column_name.strip().lower()
        self.folder = folder

        self.create_camera(deployment)

    def create_camera(self, deployment):
        self.camera_model = models.Camera()
        self.camera_model.deployment = deployment
        self.camera_model.name = self.camera_name

        # TODO: make this detected instead of default - read the angle
        self.camera_model.angle = models.Camera.DOWN_ANGLE

        self.camera_model.save()

    def create_image(self, pose, columns):
        """Create image object for this camera and given pose."""
        # create the camera if not already done...
        if self.camera_model is None:
            self.create_camera(pose.deployment)

        row_time = dateparse(columns['time'])
        pose_time = pose.date_time
        image_name = columns[self.column]

        # check that the times match... else move on
        if not row_time == pose_time:
            return None

        # it does match, create the image and return
        image = models.Image()
        image.pose = pose
        image.camera = self.camera_model

        campaign_name = pose.deployment.campaign.short_name
        deployment_name = pose.deployment.short_name
        image_path = os.path.join(self.folder, image_name)

        archive_path, webimage_path = image_import(
                campaign_name,
                deployment_name,
                image_name,
                image_path
                )

        image.web_location = webimage_path
        image.archive_location = archive_path

        image.save()

        return image


class TimeParser(csv.DictReader):
    """A class to parse CSV row by row (with a heading row).

    Contains member functions that assist in simplifying cases where
    multiple sensors/images occur in a single file."""

    def __init__(self, file_handle):
        """Create parser for open file.

        -- file_handle a file object to read from.
        The file must be csv and have a 'time' column in ISO date format.
        """

        # auto detect the dialect from an initial sample
        #dialect = csv.Sniffer().sniff(file_handle.read(1000))
        #file_handle.seek(0)
        csv.DictReader.__init__(self, file_handle)#, dialect=dialect)

        #super(TimeParser, self).__init__(file_handle)#, dialect=dialect)

        self.current_row = dict((k.lower().strip(), v) for k, v in self.next().iteritems())
        self.next_row = dict((k.lower().strip(), v) for k, v in self.next().iteritems())

        self.current_time = dateparse(self.current_row['time'])
        self.next_time = dateparse(self.next_row['time'])

        # we need the list of cameras that have image columns here
        self.cameras = []

        # we need to filter down based on cameras...
        self.camera_sensors = {}
        # but pose is generic... so no need to list things
        self.pose_sensors = []

    def register_camera(self, camera_name, angle, column_name, deployment, folder):
        camera = Camera(camera_name, angle, column_name, deployment, folder)
        self.cameras.append(
                camera
            )

        return camera.camera_model

    def register_camera_sensor(self, camera, sensor_type, column_name):
        """Register a camera/image based sensor with the parser.

        This enables measurements to be automatically applied when
        appropriate.
        """
        if not camera in self.camera_sensors:
            self.camera_sensors[camera] = []

        sensor = models.ScientificMeasurementType.objects.get(
                normalised_name=sensor_type
            )

        self.camera_sensors[camera].append(
                CameraSensor(camera, sensor, column_name)
            )

    def register_pose_sensor(self, sensor_type, column_name):
        """Register a position/time based measurement with the parser.

        This is used to easily add measurements to the pose from this
        parser (when appropriate).
        """

        sensor = models.ScientificMeasurementType.objects.get(
                normalised_name=sensor_type
            )

        self.pose_sensors.append(
                PoseSensor(sensor, column_name)
            )

    def apply_measurements(self, pose, images):
        """Apply any measurements applicable to the pose/images given.

        The pose and all images must already be saved in the database as
        extra related data is created within this function and requires
        them to have primary keys already.

        This function performs interpolation for pose/time based measurements
        but enforces that image/camera based measurements are not interpolated.

        Additionally performs other sanity checks such as images must relate
        to the current pose.
        """
        # get the rows that are either side of the pose time
        time = pose.date_time

        # so self.current_time is either equal to or greater than the
        # current pose time when the loop is done
        # there is also the implicit assumption that the next_time is
        # greater than time
        while not (self.current_time <= time < self.next_time):
            self.step()

        assert self.next_time > time, "Next Time is less than current pose time."

        for pose_sensor in self.pose_sensors:
            pose_sensor.apply_measurement(pose, self.current_time, self.current_row, self.next_time, self.next_row)

        for image in images:
            assert image.pose == pose, "Images not related to current pose."
            # only add image measurements if there are sensors for this camera
            if image.camera in self.camera_sensors:
                for image_sensor in self.camera_sensors[image.camera]:
                    image_sensor.apply_measurement(image, self.current_time, self.current_row)

    def current_image_time(self):
        if len(self.cameras) > 0:
            return self.current_time
        else:
            return datetime.datetime(datetime.MAXYEAR, 12, 31, tzinfo=tzutc())

    def next_image_time(self):
        if len(self.cameras) > 0:
            return self.next_time
        else:
            # need to include tzinfo
            return datetime.datetime(datetime.MAXYEAR, 12, 31, tzinfo=tzutc())

    def create_images(self, pose):
        """Create images for the given pose (if appropriate)."""
        time = pose.date_time

        # if we have no cameras... then no images too
        if len(self.cameras) == 0:
            return []

        assert time >= self.current_time, "Requested image creation time in past."

        # make sure we are in the correct segment
        while not (self.current_time <= time < self.next_time):
            self.step()

        # this camera didn't take an image at this time
        # so do nothing
        if self.current_time != time:
            return []

        images = []

        for cam in self.cameras:
            images.append(cam.create_image(pose, self.current_row))

        return images

    def create_pose(self, deployment, time):
        # create the pose from the columns in place here
        # there are no guarantees that this file has the pose information
        # it is merely in case it does....

        assert 'depth' in self.current_row, "Depth not in this file."
        assert 'latitude' in self.current_row, "Latitude not in this file."
        assert 'longitude' in self.current_row, "Longitude not in this file."

        assert time >= self.current_time, "Desired time in past."

        # make sure we are the correct time segment
        while not (self.current_time <= time < self.next_time):
            self.step()

        # create the pose object
        pose = models.Pose()
        pose.deployment = deployment
        pose.date_time = time

        # the times are already parsed and in place
        start_time = self.current_time
        end_time = self.next_time
        actual_time = time

        # get the deltas between the three times
        dt = (end_time - start_time).total_seconds()
        dt_start = (actual_time - start_time).total_seconds()
        dt_end = (end_time - actual_time).total_seconds()
        if end_time >= datetime.datetime(datetime.MAXYEAR-1, 1, 1, tzinfo=tzutc()):
            dt = 1.0
            dt_start = 0.0
            dt_end = 1.0

            current_row = self.current_row
            next_row = self.current_row
        else:
            current_row = self.current_row
            next_row = self.next_row

        assert dt > 0.0, "Negative time between rows."
        assert dt_start >= 0.0, "Start time after target interpolation time."
        assert dt_end > 0.0, "End time before target interpolation time."

        # now get the depth and interpolate
        start_value = float(current_row['depth'])
        end_value = float(next_row['depth'])
        pose.depth = (dt_end * start_value + dt_start * end_value) / dt

        # latitude
        start_value = float(current_row['latitude'])
        end_value = float(next_row['latitude'])
        latitude = (dt_end * start_value + dt_start * end_value) / dt

        start_value = float(current_row['longitude'])
        end_value = float(next_row['longitude'])
        longitude = (dt_end * start_value + dt_start * end_value) / dt

        pose.position = "POINT({0} {1})".format(longitude,
                                                 latitude)

        pose.save()

        return (pose, latitude, longitude)

    def step(self):
        """Return next record with lower cased keys."""
        self.current_row = self.next_row
        self.current_time = self.next_time

        try:
            next_row = self.next()
        except StopIteration:
            # we are done
            self.next_row = {}
            self.next_time = datetime.datetime(datetime.MAXYEAR, 1, 1, tzinfo=tzutc())
        else:
            self.next_row = dict((k.lower().strip(), v) for k, v in next_row.iteritems())
            self.next_time = dateparse(self.next_row['time'])



def image_import(campaign_name, deployment_name, image_name, image_path):
    """Create the web versions of the given images and return their path.

    This creates a copy of the image in jpg format and places it in the media
    location. After this it moves the raw image to archival location for long term
    storage (for feature calculation etc.).
    """

    # the location to place the original image
    archive_path = os.path.join(staging_settings.STAGING_ARCHIVE_DIR,
                                campaign_name, deployment_name, image_name)

    if staging_settings.STAGING_MOVE_ORIGINAL_IMAGES and not os.path.exists(
            os.path.dirname(archive_path)):
        try:
            os.makedirs(os.path.dirname(archive_path))
        except OSError:
            raise Exception(
                "Could not create archive location, full path: {0}".format(
                    archive_path))

    if staging_settings.STAGING_ORIGINAL_ARE_WEBIMAGES:
        if image_path.startswith(staging_settings.STAGING_WEBIMAGE_DIR):
            # we can use this image...
            webimage_location = image_path.replace(staging_settings.STAGING_WEBIMAGE_DIR, "").lstrip("/")
            return archive_path, webimage_location

    # the place to put the web version of the image
    # (converted from whatever to jpg with high quality etc.)
    image_title, original_type = os.path.splitext(image_name)
    webimage_name = image_title + '.jpg'
    # the place relative to serving root
    webimage_location = os.path.join(campaign_name, deployment_name,
                                     webimage_name)
    # absolute filesystem location
    webimage_path = os.path.join(staging_settings.STAGING_WEBIMAGE_DIR,
                                 webimage_location)

    if not os.path.exists(os.path.dirname(webimage_path)):
        try:
            os.makedirs(os.path.dirname(webimage_path))
        except OSError:
            raise Exception(
                "Could not create thumbnail location, full path: {0}".format(
                    webimage_path))

    # now actually move/convert the images
    image = cv2.imread(image_path)

    # save the web version
    # if we are wanting lowres web version... scale it down
    # calculate the nominal new size of the image to fit within 96x72px
    # (this size chosen due to 4:3 ratio, and multiples of 8)

    # target size
    target_width = staging_settings.STAGING_WEBIMAGE_MAX_SIZE[0]
    target_height = staging_settings.STAGING_WEBIMAGE_MAX_SIZE[1]

    # get original image parameters
    height, width, channels = image.shape

    # calculating scaling factor

    # if we have no target for that dimension
    # assume 1:1 scaling is used
    # that we we don't enlargen images, or have them too small
    if target_width is None:
        scale_width = 1.0
    else:
        scale_width = float(target_width) / float(width)

    if target_height is None:
        scale_height = 1.0
    else:
        scale_height = float(target_height) / float(height)

    # determine which scaling factor we want to use as we are aiming for
    # a max size take the smaller factor and use it
    if scale_width < scale_height:
        scale = scale_width
    else:
        scale = scale_height

    # a final check we are not making the image larger
    scale = min(1.0, scale)

    # scale them
    out_width = width * scale
    out_height = height * scale

    #outsize = (out_height, out_width)
    outsize = (target_width, target_height)

    # use INTER_AREA to see better shrunk results
    # use INTER_CUBIC, INTER_LINEAR for better enlargement
    # only shrink images, never increase size
    if scale < 1.0:
        image = cv2.resize(image, outsize, interpolation=cv2.INTER_AREA)
    #elif scale > 1.0:
    #    image = cv2.resize(image, outsize, interpolation=cv2.INTER_LINEAR)

    # save the web version (full size or shrunk)
    cv2.imwrite(webimage_path, image)

    # copy/move to archive
    #if staging_settings.STAGING_MOVE_ORIGINAL_IMAGES:
    #    shutil.move(image_path, archive_path)
    #else:
    #    # don't move it, just pretend to have the original...
    #    #shutil.copyfile(image_path, archive_path)
    #    pass

    # return the image details
    return archive_path, webimage_location


class DeploymentImporter(object):
    """Groups of methods relating to importing still image deployments.

    Methods check for the existence of required files, consistency of
    the internals and get handles to those files.
    """

    @classmethod
    def get_appender(cls, deployment_path):
        def get_path(file_name):
            return os.path.join(deployment_path, file_name)

        return get_path

    @classmethod
    def dependency_check(cls, deployment_path):
        """Lighweight check to see if required files exist."""

        try:
            files = cls.dependency_get(deployment_path)
        except IOError as e:
            return False
        else:
            return True

    @classmethod
    def dependency_get(cls, deployment_path):
        # shortcut to append to folder name
        get_full_path = cls.get_appender(deployment_path)

        files = {}

        # required files
        camera_file = get_full_path('cameras.csv')
        path_file = get_full_path('path.csv')
        images_folder = get_full_path('images')

        if not os.path.exists(camera_file):
            raise IOError("Cannot find camera file (cameras.csv)")

        if not os.path.exists(path_file):
            raise IOError("Cannot find path file (path.csv)")

        if not os.path.exists(images_folder):
            raise IOError("Cannot find image folder (images)")

        files['camera'] = camera_file
        files['path'] = path_file
        files['image_base'] = images_folder

        # per camera files
        camera_files = {}
        for line in csv.DictReader(open(camera_file, 'r')):
            per_camera_file = get_full_path(line['filename'].strip())
            camera_files[line['filename'].strip()] = per_camera_file
            if not os.path.exists(per_camera_file):
                raise IOError("Cannot find specified image data file ({0})".format(per_camera_file))

        files['camera_files'] = camera_files

        # optional files
        description_file = get_full_path('description.txt')

        if os.path.exists(description_file):
            files['description'] = description_file
        else:
            files['description'] = None
        # these aren't used yet...
        #image_class_file = get_full_path('whole-image-classification.csv')
        #point_class_file = get_full_path('within-image-classification.csv')

        sensors_file = get_full_path('sensors.csv')

        if os.path.exists(sensors_file):
            files['sensors'] = sensors_file
            # per sensor files
            sensor_files = {}
            for line in csv.DictReader(open(sensors_file, 'r')):
                per_sensor_file = get_full_path(line['filename'].strip())
                sensor_files[line['filename'].strip()] = per_sensor_file
                if not os.path.exists(per_sensor_file):
                    raise IOError("Cannot find specified sensor data file ({0})".format(per_sensor_file))
            files['sensor_files'] = sensor_files
        else:
            files['sensors'] = None

        return files

    @classmethod
    def import_path(cls, deployment, deployment_path):
        files = cls.dependency_get(deployment_path)
        deployment_import(deployment, files)


@transaction.commit_on_success
def deployment_import(deployment, files):
    """Import a deployment from disk.

    Certain parametesr are expected to be prefilled - namely
    short_name, campaign, license, descriptive_keywords and owner.
    The rest are obtained by information in disk.

    Information determined from on disk data include start and end time
    timestamps, start and end position, min and max depths and transect shape
    and mission_aim.
    """

    logger.debug("Entering deployment import")

    if not files['description'] is None:
        with open(files['description'], 'r') as description_file:
            deployment.mission_aim = description_file.read()
    else:
        deployment.mission_aim = "No aim given."

    deployment.min_depth = 14000.0
    deployment.max_depth = 0.0

    deployment.start_position = "POINT(0.0 0.0)"
    deployment.end_position = "POINT(0.0 0.0)"
    deployment.start_time_stamp = datetime.datetime.now()
    deployment.end_time_stamp = datetime.datetime.now()

    deployment.transect_shape = "POLYGON((0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0, 0.0 0.0))"

    # we have to save the deployment so that everything else can link to it
    logger.debug("Initial save of deployment.")
    deployment.save()

    # now we create all the file parsers that we need...

    # this holds a link to all timeparsers by file name
    parsers = {}

    # this holds a link to all camera models by camera name
    cameras = {}

    # need a hold on the pose parser
    pose_parser = TimeParser(open(files['path'], 'r'))

    # and add it to the generic parsers list
    parsers[files['path']] = pose_parser

    # image parsers
    # so one for each camera
    with open(files['camera'], 'r') as cameras_file:
        cameras_parser = csv.DictReader(cameras_file)
        for line in cameras_parser:
            # get the name of the file the images are in
            short_file_name = line['filename'].strip()
            full_file_name = files['camera_files'][short_file_name]

            name = line['name'].strip()
            column_name = line['columnname'].strip()
            angle = line['angle'].strip()

            # create a time parser for this file if not one already
            if not full_file_name in parsers:
                parsers[full_file_name] = TimeParser(open(full_file_name, 'r'))

            # now register the camera itself with the parser
            # also get a handle to the database model (needed for camera sensors)
            camera = parsers[full_file_name].register_camera(name, angle, column_name, deployment, files['image_base'])

            # add it to the mapping of cameras to their models
            cameras[name] = camera

    # sensor parsers as well
    if 'sensors' in files and files['sensors']:
        with open(files['sensors'], 'r') as sensors_file:
            sensors_parser = csv.DictReader(sensors_file)
            for line in sensors_parser:
                sensor_type = line['sensortype'].strip().lower()
                short_file_name = line['filename'].strip()
                full_file_name = files['sensor_files'][short_file_name]
                column_name = line['columnname'].strip()
                camera_name = line['camera'].strip()

                # create a time parser for this file if not one already
                if not full_file_name in parsers:
                    parsers[full_file_name] = TimeParser(open(full_file_name, 'r'))

                if not camera_name in cameras:
                    parsers[full_file_name].register_pose_sensor(sensor_type, column_name)
                else:
                    camera = cameras[camera_name]
                    parsers[full_file_name].register_camera_sensor(camera, sensor_type, column_name)

    # now we have all the parsers in parsers[] and the pose information
    # retrievable from pose_parser
    # its a matter of going through and finding when images were taken
    # creating the images

    # create a list... we will now sort by next image time
    parsers = [x for x in parsers.itervalues()]

    # sort by first image time
    parsers = sorted(parsers, key=lambda x: x.current_image_time())

    image_time = parsers[0].current_image_time()

    # things needed to get proper stats for the deployment
    first_pose = None
    last_pose = None

    lat_lim = LimitTracker()
    lon_lim = LimitTracker()

    logger.debug("Progressing through time data.")
    # the time at which we are done... ie when all next times exceed this
    end_time = datetime.datetime(datetime.MAXYEAR, 1, 1, tzinfo=tzutc())
    while image_time < end_time:
        pose, latitude, longitude = pose_parser.create_pose(deployment, image_time)
        images = []

        # go through and get all images
        for p in parsers:
            images.extend(p.create_images(pose))

        # now get all pose/image measurements
        for p in parsers:
            p.apply_measurements(pose, images)

        # now get the next time...
        parsers = sorted(parsers, key=lambda x: x.next_image_time())

        image_time = parsers[0].next_image_time()

        # we want to track first and last pose
        last_pose = pose
        if first_pose is None:
            first_pose = pose

        # for the transect shape
        lat_lim.check(latitude)
        lon_lim.check(longitude)

        # and min/max depth
        if pose.depth > deployment.max_depth:
            deployment.max_depth = pose.depth

        if pose.depth < deployment.min_depth:
            deployment.min_depth = pose.depth

    # at this point we are done with image creation
    # so need to wrap up deployment creation and return
    deployment.start_time_stamp = first_pose.date_time
    deployment.end_time_stamp = last_pose.date_time

    deployment.start_position = first_pose.position
    deployment.end_position = last_pose.position

    deployment.transect_shape = "POLYGON(({0} {2}, {0} {3}, {1} {3}, {1} {2}, {0} {2} ))".format(
        lon_lim.minimum,
        lon_lim.maximum,
        lat_lim.minimum,
        lat_lim.maximum)

    # save and done!
    logger.debug("Final save of deployment.")
    deployment.save()
