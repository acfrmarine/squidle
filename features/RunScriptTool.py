import json
import os
import cPickle as pickle
import random
import scipy
import string
import tarfile
import traceback
from django.core import serializers
import sys
from catamidb.models import Image
import logging
import datetime
from features import FeaturesErrors
import pysftp

__author__ = 'marrabld'
# TODO: This is getting untidy.  Might be better to have a Super class with
# protected methods libfeatuer and libcluster inherit.  Rather than having
# static helper methods.  There is too much replication of code and things
# aren't logically across the classes.
# The more I look at this the more I don't like it.  its a mess :-(

logger = logging.getLogger(__name__)


class DeployJobTool():
    """ This tool is designed build launch libcluster or libfeature on Epic

    or any computer running Torque and libcluster/libfeature.  We put all of the
    data here and only write the data to file that the particular lib needs.  I.e.
    try and make the tool agnostic to the lib its running.

    Example use:

    import features.RunScriptTool as DJT
    a = DJT.DeployJobTool()
    a.image_primary_keys = ['00000001','00000002'] #dummpy keys
    a.make_image_list()
    server = pysftp.Connection(rst.server_ip, username=user_name, password=user_password)
    a.deploy_job('libfeature')
    """

    def __init__(self):
        """ default class parameters for the job"""
        #====================
        # PARAMETERS FOR LIBCLUSTER/LIBFEATURE
        #====================

        self.cluster_granularity = 1
        self.verbose_output = True
        self.nthreads = 1
        self.dimensionality = 20
        self.algorithm = 'BGMM'
        # The images we would like to cluster/feature
        self.image_primary_keys = []
        self.image_location = []
        self.user_name = 'Anon'
        self.user_password = ''

        self.job_id = self.id_generator()

        logger.debug('job_id is :: ' + self.job_id)
        self.job_dir = ('/tmp/CATAMI/features/' + self.user_name + '/' + self.
        job_id)
        os.makedirs(self.job_dir)
        # TODO : need to parse user id from the front end of the person that is
        # logged in  This will be a list of deployments after querying based on
        # image list might leave this out for now 06/02/13 Dan M
        # deployment_information = []

    def write_json_file(self, fname='meta.json'):

        parameter_dict = {'cluster_granularity': self.cluster_granularity,
                          'verbose_output': self.verbose_output,
                          'nthreads': self.nthreads,
                          'dimensionality': self.dimensionality,
                          'algorithm': self.algorithm,
                          'image_primary_keys': self.image_primary_keys,
                          'image_location': self.image_location}

        f = open(self.job_dir + '/' + fname, 'wb')

        logger.debug('Writing ' + fname + ' to disk at location :: ' + self.
        job_dir)
        f.write(json.dumps(parameter_dict))

    def write_rand_numpy_array_to_disk(self, dim=(1, 20)):
        """This is mostly for testing and debugging

        This will generate a random vector that will simulate the features vector
        dim is the require dimensions r,c
        Returns : numpy.array
        """

        for im in self.image_primary_keys:
            if dim[0] == 1:
                feature = scipy.rand(dim[1])
            else:
                feature = scipy.rand(dim[0], dim[1])

            logger.debug('Writing numpy array to :: ' + self.job_dir + '/' +
                         str(im) + '.p')
            pickle.dump(feature, open(self.job_dir + '/' + str(im) + '.p',
                                      'wb'))

    def compress_files(self, fname='features', **kwargs):
        """

        do_zip [True] :: compress or not.
        compression_type [gz] :: gz or bz

        :param kwargs:
        :return:
        """

        compression_type = kwargs.get('compression_type', 'gz')
        do_zip = kwargs.get('do_zip', True)

        tar = tarfile.open(self.job_dir +
                           '/' +
                           fname +
                           '.tar.' +
                           compression_type,
                           'w:' +
                           compression_type)

        tar.add(self.job_dir + '/meta.json', arcname='/meta.json')
        for im in self.image_primary_keys:
            tar.add(self.job_dir + '/' + str(im) + '.p', arcname=str(im) +
                                                                 '.p')

        tar.close()

        #def push_files_to_server(self):
    #    pass

    def id_generator(self, size=12, chars=string.ascii_uppercase + string.
    digits):
        return ''.join(random.choice(chars) for x in range(size))

    def make_image_list(self):
        """ Queries the database for the image locaitons based on the pks"""
        for image in self.image_primary_keys:
            self.image_location.append(Image.objects.get(pk=image).
            archive_location)

    def deploy_job(self, server=object, job_type='libfeature'):
        """writes the reuqired scripts for the job, pushes them to the jobserver

        and launches the job
        """

        rst = RunScriptTool()
        rst.feature_image_dir = (rst.scratch_directory + '/' + self.job_id +
                                 '/img/')
        rst.feature_output_dir = (rst.scratch_directory + '/' + self.job_id +
                                  '/output/')
        # self.server = pysftp.Connection(rst.server_ip,
        # username=self.user_name, password=self.user_password)

        if job_type == 'libfeature':
            # make the directory on scratch
            self.server = server
            # pysftp.Connection(rst.server_ip, username=self.user_name,
            # password=self.user_password, log=True)

            rst.library = 'libfeature'
            self.write_json_file('meta.json')
            rst.write_libfeature_script(self.job_dir + '/run_libfeature.py')
            rst.write_pbs_script(self.job_dir + '/queue_libfeature.pbs',
                                 jobid=self.job_id)

            file_list = [rst.libfeature_run_file, rst.run_file, self.job_dir +
                                                                '/meta.json']
            print file_list
            ServerTool.compress_files(file_list, self.job_dir + '/job')

            try:
                ServerTool.push_file_to_server(self.job_dir + '/job.tar.gz',
                                               rst.server_ip, self.server)
                self.server.execute('mkdir ' + rst.scratch_directory + '/' +
                                    self.job_id)
                self.server.execute('mkdir ' + rst.feature_output_dir)
                self.server.execute('mkdir ' + rst.feature_image_dir)
                self.server.execute('cp job.tar.gz ' + rst.scratch_directory +
                                    '/' + self.job_id)
                self.server.chdir(rst.scratch_directory + '/' + self.job_id)
                self.server.execute(rst.scratch_directory + '/' + self.job_id)
                self.server.execute('tar -xzvf ' + rst.scratch_directory +
                                    '/' +
                                    self.job_id +
                                    '/job.tar.gz --directory=' +
                                    rst.scratch_directory +
                                    '/' +
                                    self.job_id)
            except:
                logger.error('Failed to PUT :: ' +
                             self.job_dir + 'job.tar.gz' +
                             ' to server')

                raise FeaturesErrors.ConnectionError('Failed to put ',
                                                     'Failed to PUT :: ' + self.job_dir + 'job.tar.gz' +
                                                     'to server :: ')

        elif job_type == 'libcluster':
            #rst.write_libcluster_script()
            pass
            #TODO : Write this!!
        #rst.write_pbs_script()

        # push to server
        #rst.push_pbs_script_to_server(self.server,start_job=False)
        self.server.execute('qsub ' + rst.scratch_directory + '/' + self.
        job_id + '/queue_libfeature.pbs')
        self.server.execute('qstat')

        # clean up


class RunScriptTool():
    """ This tool is designed to generate the pbs script for queuing libCluster
    http://www.clusterresources.com/products/torque/docs10/a.hlicense.txt

    """

    def __init__(self, username='user', password=''):
        """Default class parameters for the runscript"""

        #====================
        # PARAMETERS FOR THE RUN SCRIPT
        #====================
        self.pbs_workgroup = 'partner464'  # workgroup for CATAMI

        #====================
        # JOB QUEUE TYPE
        #--------------------
        # http://portal.ivec.org/docs/PBS_Pro_on_Epic
        # available are routequeue,largeq,mediumq,smallq,
        # longq,copyq,debugq,testq
        #====================
        self.job_queue = 'routequeue'
        self.wall_time = datetime.time(12, 0, 0)  # Max job time
        self.memory = 23  # required RAM in gigabytes
        self.num_nodes = 1
        self.num_cpus = 12
        self.scratch_directory = ('/scratch/' + self.pbs_workgroup +
                                  '/catamihpc')
        self.run_file = 'catami.pbs'  # default script name
        self.library = 'libCluster'  # ie clustering, features etc

        #====================
        # PARAMETERS FOR THE RUN SERVER
        #====================
        self.server_ip = 'epic.ivec.org'
        self.server_username = username
        self.server_password = password

        #====================
        # PARAMETERS FOR libfeatures
        #====================
        self.libfeature_run_file = 'run_feature.py'
        self.feature_image_dir = self.scratch_directory
        # need to set this from deploy tool
        self.feature_output_dir = self.scratch_directory + '/output/'

    def write_libfeature_script(self, file_name='run_libfeature.py'):
        """Write the python script that runs libfeature."""

        self.libfeature_run_file = file_name
        f = open(self.libfeature_run_file, 'w')

        logger.debug('Writing libfeature run file :: ' + self.
        libfeature_run_file)

        f.write('#! /usr/bin/env python' + '\n'
                                           'import glob' + '\n'
                                                           'import os' + '\n'
                                                                         'import json' + '\n'
                                                                                         'from extractors.extractor import extractor' + '\n'
                                                                                                                                        'from descriptors.testdesc import TestDesc' + '\n'
                                                                                                                                                                                      'features = json.load(open(meta.json))' + '\n'
                                                                                                                                                                                                                                'imgdir = \'' + self.feature_image_dir + '\'' + ' \n'
                                                                                                                                                                                                                                                                                'savedir = \'' + self.feature_output_dir + '\' \n'
                                                                                                                                                                                                                                                                                                                           'filelist = glob.glob(imgdir + \'*.jpg\')' + '\n'
                                                                                                                                                                                                                                                                                                                                                                        'os.chdir(\'' + self.feature_image_dir + '\')' + '\n' # work around for not knowing the unique id
                                                                                                                                                                                                                                                                                                                                                                                                                         'for im in features.filelist:' + '\n'
                                                                                                                                                                                                                                                                                                                                                                                                                                                          '    os.system(\"wget \' + im + \' \")' + '\n'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    'os.chdir(/home/catamihpc/bin/libfeature)' + '\n'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 'desc = TestDesc()' + '\n'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       'extractor(filelist, savedir, desc)'
        )

        f.close()

        #def write_libcluster_script(self):
    #    pass

    def write_pbs_script(self, file_name='queue_libfeature.pbs', jobid=''):
        """Writes the parameters to a pbs script

        queues a job on a pbs server"""

        self.run_file = file_name
        f = open(self.run_file, 'w')

        logger.debug('Writing pbs script :: ' + self.run_file)

        f.write('#!/bin/bash' + '\n' '# pbs file generated by catamiPortal' +
                '\n' '#PBS -W group_list=' + self.pbs_workgroup + '\n' '#PBS -q '
                + self.job_queue + '\n' '#PBS -l walltime=' + str(self.wall_time)
                + '\n' '#PBS -l select=' + str(self.num_nodes) + ':ncpus=' + str(
            self.num_cpus) + ':mem=' + str(self.memory) + 'gb' '\n' 'cd ' +
                self.scratch_directory + '/' + jobid + '\n' '\n'
                                                       'module load python' + '\n' 'python ' + self.scratch_directory +
                '/' + jobid + '/run_libfeature.py' + '\n' + '\n')
        #TODO change this line to include libcluster

        f.close()

    def push_pbs_script_to_server(self, server=object, password='',
                                  start_job=True):
        """
        Pushes the run script to the server and initiate the job

        :param password: Password for the server
        :return:
        """

        # TODO : Figure out what files to push with the script

        # SCP over the pbs sript
        logger.debug('copying file :: ' +
                     self.run_file + ' to :: ' +
                     self.server_ip)

        try:
            server.put(self.run_file)
        except:
            logger.error('Failed to PUT :: ' +
                         self.run_file +
                         ' to server :: ' +
                         self.server_ip)

            raise FeaturesErrors.ConnectionError('Failed to put ',
                                                 'Failed to PUT :: ' +
                                                 self.run_file +
                                                 'to server :: ' +
                                                 self.server_ip)

        if start_job:
            # Queue the job
            logger.debug('Sending job request')
            try:
                server.execute('qsub ' + self.run_file)
            except:
                logger.error('Failed to submit job :: ' + self.run_file)
                raise FeaturesErrors.ConnectionError('Failed to start ',
                                                     'Failed to submit job :: ' +
                                                     self.run_file)

        server.close()


class ServerTool():
    """ Some helper methods for parsing files to runserver"""

    @staticmethod
    def compress_files(file_list, fname, do_zip=True, compression_type='gz',
                       **kwargs):
        """


        :param file_list:
        :param fname:
        :param do_zip:
        do_zip [True] :: compress or not.
        compression_type [gz] :: gz or bz

        :param kwargs:
        :return:
        """

        compression_type = compression_type
        do_zip = do_zip

        tar = tarfile.open(fname +
                           '.tar.' +
                           compression_type,
                           'w:' +
                           compression_type)

        for fname in file_list:
            tar.add(fname, arcname=os.path.basename(fname))

        tar.close()

    @staticmethod
    def push_file_to_server(job_file, server_ip, server=object,
                            start_job=False):
        """
        Pushes the run script to the server and initiate the job

        :param self:
        :param job_file:
        :param server_ip:
        :param server:
        :param start_job:
        :return:
        """

        # SCP over the pbs script
        logger.debug('copying file :: ' +
                     job_file + ' to :: ' +
                     server_ip)

        try:
            server.put(job_file)
        except:
            logger.error('Failed to PUT :: ' +
                         job_file +
                         ' to server :: ' +
                         server_ip)
            traceback.print_exc(file=sys.stdout)

            raise FeaturesErrors.ConnectionError('Failed to put ',
                                                 'Failed to PUT :: ' +
                                                 job_file +
                                                 'to server :: ' +
                                                 server_ip)

        if start_job:
            # Queue the job
            logger.debug('Sending job request')
            try:
                server.execute('qsub ' + job_file)
            except:
                logger.error('Failed to submit job :: ' + job_file)
                traceback.print_exc(file=sys.stdout)
            raise FeaturesErrors.ConnectionError('Failed to start ',
                                                 'Failed to submit job :: ' +
                                                 job_file)

        server.close()
