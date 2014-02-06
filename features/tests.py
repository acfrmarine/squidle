"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import json
import os
from paramiko import AuthenticationException
import tarfile

from django.test import TestCase
from mock import Mock
from catamidb.models import Image
from features import FeaturesErrors
import features
from features.RunScriptTool import RunScriptTool, DeployJobTool, ServerTool
from dbadmintool.administratorbot import Robot
import logging
from model_mommy import mommy
from django.contrib.gis.geos import Point, Polygon

logger = logging.getLogger(__name__)


def create_setup(self):
    self.campaign_one = mommy.make_one('catamidb.Campaign', id=1)

    self.deployment_one = mommy.make_one('catamidb.Deployment',
            start_position=Point(12.4604, 43.9420),
            end_position=Point(12.4604, 43.9420),
            transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
            id=1,
            campaign=self.campaign_one
        )
    self.deployment_two = mommy.make_one('catamidb.Deployment',
            start_position=Point(12.4604, 43.9420),
            end_position=Point(12.4604, 43.9420),
            transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
            id=1,
            campaign=self.campaign_one
        )

    self.pose_one = mommy.make_one('catamidb.Pose',
            position=Point(12.4, 23.5),
            id=1,
            deployment=self.deployment_one
        )
    self.pose_two = mommy.make_one('catamidb.Pose',
            position=Point(12.4, 23.5),
            id=2,
            deployment=self.deployment_two
        )

    self.camera_one = mommy.make_one('catamidb.Camera',
            deployment=self.deployment_one,
            id=1,
        )
    self.camera_two = mommy.make_one('catamidb.Camera',
            deployment=self.deployment_two,
            id=1,
        )

    self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
    self.mock_image_one = mommy.make_one('catamidb.Image',
            pose=self.pose_one,
            camera=self.camera_one,
            web_location=self.image_list[0],
            pk=1
        )
    self.mock_image_two = mommy.make_one('catamidb.Image',
            pose=self.pose_two,
            camera=self.camera_two,
            web_location=self.image_list[1],
            pk=2
        )

    image_objects = Image.objects.all()
    for image in image_objects:
        self.djt.image_primary_keys.append(image.pk)


class DeployJobTest(TestCase):
    """Tests for the DeployJobTool"""

    def setUp(self):

        self.djt = DeployJobTool()
        self.server = Mock()
        #self.djt.image_primary_keys = ['00000001','00000002']

        # for bender.check_sum_file method
        self.bender = Robot()

        create_setup(self)

    def test_write_json_file(self):
        """Check the json file writer works"""

        # Check it writes to disk correctly
        self.djt.write_json_file()
        mock_write_check = self.bender.check_sum_file(self.djt.job_dir +
            '/meta.json')
        mock_fixture_check = self.bender.check_sum_file(
            'features/fixtures/mock_features.json')
        self.assertTrue(mock_fixture_check == mock_write_check)

        # Check the file format by reading it back in and checking the values
        json_features = json.load(open(self.djt.job_dir + '/meta.json'))

        self.assertTrue(json_features['cluster_granularity'] == 1)
        self.assertTrue(json_features['verbose_output'] == True)
        self.assertTrue(json_features['nthreads'] == 1)
        self.assertTrue(json_features['dimensionality'] == 20)
        self.assertTrue(json_features['algorithm'] == 'BGMM')
        self.assertTrue(json_features['image_primary_keys'] == self.djt.
            image_primary_keys)

    def test_write_rand_numpy_array_to_disk(self):
        """Test that we can write fake feature vectors to disk"""
        # they're random so not sure how to non trivially check them.
        # infact their values don't matter so I just check they are crecated

        self.djt.write_rand_numpy_array_to_disk()

        #check they are on disk
        for im in self.djt.image_primary_keys:
            self.assertTrue(os.path.exists(self.djt.job_dir + '/' + str(im) +
                '.p'))

        self.djt.write_rand_numpy_array_to_disk(dim=(2, 20))

        #check they are on disk
        for im in self.djt.image_primary_keys:
            self.assertTrue(os.path.exists(self.djt.job_dir + '/' + str(im) +
                '.p'))

    def test_compress_files(self):
        """Test that we can compress files in a tarball"""

        # Need to write the files before compressing them
        self.djt.write_rand_numpy_array_to_disk()
        self.djt.write_json_file()
        self.djt.compress_files()

        # Check the file is there
        self.assertTrue(os.path.exists(self.djt.job_dir + '/' +
            'features.tar.gz'))

        # Check the files are in the tarball
        tar = tarfile.open(self.djt.job_dir + '/' + 'features.tar.gz', "r")
        tar_list = tar.getnames()

        self.assertTrue(tar_list[0] == 'meta.json')
        self.assertTrue(tar_list[1] == str(self.djt.image_primary_keys[0]) +
            '.p')
        self.assertTrue(tar_list[2] == str(self.djt.image_primary_keys[1]) +
            '.p')

    def test_make_image_list(self):
        """ Make sure the method makes the correct list of image locations"""
        self.djt.make_image_list()

        i = 0
        logger.debug(self.djt.image_location)
        for image in self.image_list:
            self.assertTrue(self.djt.image_location[i])
            i += 1

    def test_deploy_job(self):
        """
        :return:
        """

        self.assertIsNone(self.djt.deploy_job(self.server))
        self.assertIsNone(self.djt.deploy_job(self.server,
            job_type='libcluster'))
        # this hasn't been written yet

    def test_noconnect_deploy_job(self):

        self.server.put.side_effect = AuthenticationException("Testing")

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.ConnectionError,
        # self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!
        try:
            self.djt.deploy_job(self.server)
        except features.FeaturesErrors.ConnectionError as e:
            connection_error_occured = True

        self.assertTrue(connection_error_occured)


class RunScriptTest(TestCase):
    """Test for the RunScriptTool"""

    def setUp(self):

        mock_user = 'test'
        mock_password = 'test'

        self.server = Mock()
        self.rst = RunScriptTool()

        # for bender.check_sum_file method
        self.bender = Robot()

    def test_write_pbs_script(self):
        """Check that the code writes the correct pbs script"""
        self.rst.write_pbs_script(file_name='/tmp/queue_libfeature.pbs')
        mock_write_check = self.bender.check_sum_file(self.rst.run_file)
        mock_fixture_check = self.bender.check_sum_file(
            'features/fixtures/mock_pbs_script.pbs')
        self.assertTrue(mock_fixture_check == mock_write_check)

    def test_write_libfeature_script(self):
        """Check that the code writes the correct python  script

        for running libfeature
        """
        self.rst.write_libfeature_script(file_name='/tmp/run_libfeature.py')
        mock_write_check = self.bender.check_sum_file(
            self.rst.libfeature_run_file)
        mock_fixture_check = self.bender.check_sum_file(
            'features/fixtures/mock_run_feature.py')
        self.assertTrue(mock_fixture_check == mock_write_check)

    def test_push_pbs_script_to_server(self):
        # Test normal operation
        self.assertIsNone(self.rst.push_pbs_script_to_server(self.server))

    def test_server_calls_push_pbs_script_to_server(self):
        """Test to make sure that put and execute are called at least once"""
        self.rst.push_pbs_script_to_server(self.server)
        self.server.put.assert_called_once_with('catami.pbs')
        self.server.close.assert_called_once_with()

    def test_server_put_push_pbs_script_to_server(self):
        # Test that user name or possword is incorrect
        # force the username and/or password to be incorrect
        self.server.put.side_effect = AuthenticationException("Testing")

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.ConnectionError,
        # self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!
        try:
            self.rst.push_pbs_script_to_server(self.server)
        except features.FeaturesErrors.ConnectionError as e:
            connection_error_occured = True

        self.assertTrue(connection_error_occured)

    def test_server_execute_push_pbs_script_to_server(self):
        """Test to see that the correct exception is raised

         if we cant kick pbs"""

        # Force a startjob fail.
        self.server.execute.side_effect = Exception("Testing")

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.
        # ConnectionError,self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!

        try:
            self.rst.push_pbs_script_to_server(self.server)
        except features.FeaturesErrors.ConnectionError as e:
            execute_error_occured = True

        self.assertTrue(execute_error_occured)


class ServerToolTest(TestCase):

    def setUp(self):

        """Test that we can compress files in a tarball"""

        mock_user = 'test'
        mock_password = 'test'

        self.server = Mock()
        self.rst = RunScriptTool()
        self.djt = DeployJobTool()

        self.test_file = '/tmp/CATAMI/features/Anon/tmp.txt'

        create_setup(self)

    def test_compress_files(self):

        # Need to write the files before compressing them
        self.djt.write_rand_numpy_array_to_disk()
        self.djt.write_json_file()
        file_list = []

        file_list.append(self.djt.job_dir + '/meta.json')

        for i in range(2):
            #file_list.append(str(self.djt.image_primary_keys[i]) + '.p')
            file_list.append(self.djt.job_dir + '/' + str(self.djt.
                image_primary_keys[i]) + '.p')

        logger.debug(file_list)

        ServerTool.compress_files(file_list, self.djt.job_dir + '/features')

        # Check the file is there
        self.assertTrue(os.path.exists(self.djt.job_dir + '/features.tar.gz'))

        # Check the files are in the tarball
        tar = tarfile.open(self.djt.job_dir + '/' + 'features.tar.gz', "r")
        tar_list = tar.getnames()

        self.assertTrue(tar_list[0] == 'meta.json')
        self.assertTrue(tar_list[1] == str(self.djt.image_primary_keys[0]) +
            '.p')
        self.assertTrue(tar_list[2] == str(self.djt.image_primary_keys[1]) +
            '.p')

    def test_push_file_to_server(self):

        f = open(self.test_file, 'wb')
        f.write('blah')
        self.assertIsNone(ServerTool.push_file_to_server(self.test_file,
            'catami.ivec.org', self.server, start_job=False))

    def test_server_calls_push_pbs_script_to_server(self):
        """Test to make sure that put and execute are called at least once"""
        ServerTool.push_file_to_server(self.test_file, 'catami.ivec.org', self
            .server, start_job=False)
        self.server.put.assert_called_once_with(self.test_file)
        self.server.close.assert_called_once_with()

    def test_server_put_push_pbs_script_to_server(self):
        # Test that user name or possword is incorrect
        # force the username and/or password to be incorrect
        self.server.put.side_effect = AuthenticationException("Testing")
        connection_error_occured = False

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.ConnectionError,
        # self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!
        try:
            ServerTool.push_file_to_server(self.test_file,
                                           'catami.ivec.org',
                                           self.server, start_job=False)
        except features.FeaturesErrors.ConnectionError as e:
            connection_error_occured = True

        self.assertTrue(connection_error_occured)

    def test_server_execute_push_pbs_script_to_server(self):
        """Test to see that the correct exception is raised

         if we cant kick pbs"""

        # Force a startjob fail.
        self.server.execute.side_effect = Exception("Testing")
        execute_error_occured = False

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.
        # ConnectionError,self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!

        try:
            ServerTool.push_file_to_server(self.test_file,
                                               'catami.ivec.org',
                                               self.server, start_job=True)
        except features.FeaturesErrors.ConnectionError as e:
            execute_error_occured = True

        self.assertTrue(execute_error_occured)
