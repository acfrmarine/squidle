"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError

from django.core.serializers.base import DeserializationError

from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase, TestApiClient
from model_mommy import mommy

from django.forms import FloatField, TextInput, SplitDateTimeField

from .auvimport import LimitTracker, NetCDFParser, TrackParser
from . import deploymentimport

from catamidb.models import Campaign, Deployment, ScientificMeasurementType

import datetime
from dateutil.tz import tzutc


def setup_login(self):
    # create a testing user
    self.username = 'testing'
    self.email = 'testing@example.com'
    self.password = User.objects.make_random_password()
    self.login = {'identification': self.username, 'password': self.password}

    self.login_url = '/accounts/signin/?next='

    # this creates the testing user and saves it
    self.user = User.objects.create_user(self.username, self.email,
                                         self.password)

class AUVImportTools(TestCase):
    """Test the components in auvimport.py."""

    def test_limit_tracker(self):
        """Test LimitTracker used in auvimport."""

        # check direct values
        direct_track = LimitTracker()

        direct_track.check(1.0)

        self.assertEqual(direct_track.minimum, 1.0)
        self.assertEqual(direct_track.maximum, 1.0)

        direct_track.check(10.0)
        direct_track.check(-10.0)

        self.assertEqual(direct_track.minimum, -10.0)
        self.assertEqual(direct_track.maximum, 10.0)

        # check values in a dictionary
        dict_value_track = LimitTracker('val')

        dict_value_track.check({'val': 1.0})

        self.assertEqual(dict_value_track.minimum, 1.0)

        dict_value_track.check({'val': 10.0})
        dict_value_track.check({'val': -10.0})

        self.assertEqual(dict_value_track.maximum, 10.0)
        self.assertEqual(dict_value_track.minimum, -10.0)

        # the final (odd) cases
        # should throw error... or silently ignore?

        # using a dict, but give it a value
        self.assertRaises(TypeError, dict_value_track.check, (20.0))
        # or a dict with the wrong key
        dict_value_track.check({'other': -20.0})

        self.assertEqual(dict_value_track.maximum, 10.0)
        self.assertEqual(dict_value_track.minimum, -10.0)

        # using a value but give it a dict
        self.assertRaises(TypeError, direct_track.check, ({'val': 20.0}))

        self.assertEqual(direct_track.minimum, -10.0)
        self.assertEqual(direct_track.maximum, 10.0)

    def test_netcdf_parser(self):
        """Test NetCDFParser used in auvimports."""
        netcdf_file = open(
            'staging/fixtures/IMOS_AUV_ST_20090611T063544Z_SIRIUS_FV00.nc',
            'r')

        # test that opening works and that we can get a value
        netcdf_parser = NetCDFParser(netcdf_file)
        val = netcdf_parser.next()

    def test_track_parser(self):
        """Test TrackParser used in auvimports."""
        track_file = open(
            'staging/fixtures/freycinet_mpa_03_reef_south_latlong.csv', 'r')

        # test that opening works and we can get a value
        track_parser = TrackParser(track_file)
        val = track_parser.next()

        self.assertTrue("year" in val)


class DeploymentImport(ResourceTestCase):
    """Test the generic still image importer."""

    def setUp(self):
        """Setup requirements for DeploymentImporting."""
        super(DeploymentImport, self).setUp()

        # create a client and a user to work with
        self.api_client = TestApiClient()

        self.username = 'Bob'
        self.password = 'password'
        self.email = 'bob@example.com'

        self.user = User.objects.create_user(
                self.username,
                self.email,
                self.password
            )

        self.api_client.client.login(
                username=self.username,
                password=self.password
            )

        self.campaign = mommy.make_one('catamidb.Campaign', id=1)

        # get the local directory of this file
        # relative to this are the fixtures
        # that we need to import from
        import os
        import os.path

        self.local_dir = os.path.dirname(os.path.abspath(__file__))

        # get the fixture paths
        pass_path = os.path.join(self.local_dir, 'fixtures/fake_deployment')

        self.deployment_path = pass_path

    def test_dependency_check(self):
        """Test the dependency check class method of DeploymentImporter."""
        import os.path

        pass_path = self.deployment_path
        fail_path = os.path.join(self.local_dir, 'fixtures/fake_auv_deployment')

        # and test the check
        self.assertTrue(
                deploymentimport.DeploymentImporter.dependency_check(pass_path),
                "'{0}' did not pass check".format(pass_path)
            )
        self.assertFalse(
                deploymentimport.DeploymentImporter.dependency_check(fail_path),
                "'{0}' passed check".format(fail_path)
            )

    def test_deployment_import(self):
        """Test the actual import code."""

        # create a few measurement types needed for this
        cadence = ScientificMeasurementType()

        cadence.normalised_name = "cadence"
        cadence.display_name = "Cadence"
        cadence.max_value = 200
        cadence.min_value = 0
        cadence.description = "How fast you pedal"
        cadence.units = 'm'

        cadence.save()

        index = ScientificMeasurementType()

        index.normalised_name = "index"
        index.display_name = "Index"
        index.max_value = 100000
        index.min_value = 0
        index.description = "Number of the Image"
        index.units = "m"

        index.save()

        # get the fixture path
        path = self.deployment_path

        # prefill what we need to
        deployment = Deployment()

        deployment.short_name = "TestDeployment"
        deployment.campaign = self.campaign
        deployment.license = "CC-BY"
        deployment.descriptive_keywords = "Test Keyword, Other Keyword"

        # and fire it off!
        # this should throw nothing
        deploymentimport.DeploymentImporter.import_path(deployment, path)

        # now check it worked!

        # there are 16 image pairs
        self.assertEqual(deployment.pose_set.count(), 16)

        for p in deployment.pose_set.all():
            # check the correct number of images per pose
            self.assertEqual(p.image_set.count(), 2)

            # check the cadence pose measurement came through
            self.assertEqual(p.scientificposemeasurement_set.count(), 1)

            cadence_m = p.scientificposemeasurement_set.get(measurement_type__normalised_name="cadence")

            # get the front image
            front = p.image_set.get(camera__name="Front")

            # check it has an index measurement
            self.assertEqual(front.scientificimagemeasurement_set.count(), 1)

            index_m = front.scientificimagemeasurement_set.get(measurement_type__normalised_name="index")
