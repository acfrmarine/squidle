"""A bot to check database integrity and manage backups
"""

__author__ = "Dan Marrable"
import traceback
import sys
import logging
import tarfile
import hashlib
import os
from shutil import copyfile
from django.db import connections
from django.db.utils import ConnectionDoesNotExist
from django.core import management
from datetime import datetime
from StringIO import StringIO
from catamidb.models import *
from dbadmintool.models import DataLogger
from django.db import connection, transaction

logger = logging.getLogger(__name__)


class Robot():
    """Base class for the adminitrator bot"""

    def __init__(self):
        """class constructor for setting up the bot parameters"""
        # how often to poll the server for connection in sec
        self.dt_connection = 10 # not used, using cron instead

    def check_database_connection(self, dbname='catamidb'):
        """Check to see if database connection is open. Return True or False
The return is true if connection is open false if connection failed
"""

        try:
            cursor = connections[dbname].cursor()

            if cursor:
                logger.debug('Connection open to database :: ' + dbname)
                return True

        except ConnectionDoesNotExist:
            logger.error('Cannot connect to database :: ' +
                         dbname + ' :: Query failed')
            return False

    def make_local_backup(self, dbname='catamidb', **kwargs):
        """Do a naive backup to local machine

Keywords include:

directory [./dbadmintool/backup/] :: The directory to backup to.
do_zip [True] :: compress or not.
compression_type [gz] :: gz or bz2
file_format [json] :: raw data output fomat. :: json, xml, yaml
unit_test [off] :: set to test corruption procedure :: off, corrupt
"""

        # Extract any kwargs that are parsed

        # default to current dir '.'
        directory = kwargs.get('directory', './dbadmintool/backup/')
        compression_type = kwargs.get('compression_type', 'gz')
        do_zip = kwargs.get('do_zip', True)
        file_format = kwargs.get('file_format', 'json')
        unit_test = kwargs.get('unit_test', 'off')

        #assume our unit tests are true unless otherwise failed
        test = {'checksum': True, 'archive': True, 'copy': True}

        # Setup the files to write data to.
        fname = str(datetime.now()) + '-' + dbname + '.bak'

        # Catch the data from dumpdata on the stdio
        content = StringIO()
        management.call_command('dumpdata', stdout=content, interactive=False,
                                format=file_format)
        content.seek(0)
        data = content.read()

        # Zip up the data
        if do_zip:
            tmp_directory = '/tmp/'
            # let the os delete later.
            tmpfile = open(tmp_directory + fname, 'w')
            tar = tarfile.open(directory +
                               fname +
                               '.tar.' +
                               compression_type,
                               'w:' +
                               compression_type)
            tmpfile.write(data)
            tmpfile.close()
            tar.add(tmp_directory + fname, arcname=fname)
            tar.close()

            # Make a copy of the backup, extract it and check sum
            copyfile(directory + fname + '.tar.' + compression_type,
                     directory + 'copy_' + fname + '.tar.' + compression_type)

            #compare the two copied files
            chk_file = self.check_sum_file(directory + fname + '.tar.'
                                           + compression_type)
            logger.debug(directory + fname +
                         '.tar.' +
                         compression_type +
                         ' Checksum :: ' +
                         str(chk_file))

            chk_copy = self.check_sum_file(directory + 'copy_' +
                                           fname + '.tar.'
                                           + compression_type)

            # For testing we intentionally corrupt the data
            if unit_test == 'corrupt':
                chk_copy = '0000000000000'

            logger.debug(directory + 'copy_'
                         + fname + '.tar.' +
                         compression_type +
                         ' Checksum :: ' +
                         str(chk_file))

            if chk_file == chk_copy:
                logger.debug('backup archive copied correctly')
                test['checksum'] = True
            else:
                logger.error('backup archive check sum fail')
                #return False
                test['checksum'] = False

            # Check to see if file is in the archive
            tar = tarfile.open(directory +
                               'copy_' +
                               fname +
                               '.tar.' +
                               compression_type,
                               'r:' + compression_type)

            for tarinfo in tar:
                logger.debug(tarinfo.name + " is" +
                             str(tarinfo.size) +
                             " bytes in size")

            if unit_test == 'corrupt':
                tar_name = '000000'
            else:
                tar_name = tarinfo.name

            if tar_name == fname:
                logger.debug('File name in archive matches backup file')
                test['archive'] = True
            else:
                logger.error('File name in archive does not match backup file')
                #return False
                test['archive'] = False

            # Extract the data file from the copied archive and
            # checksum against the original
            tar.extractall(path=directory)
            chk_file = self.check_sum_file(directory + fname)
            logger.debug(directory + fname + ' Checksum :: ' + str(chk_file))
            chk_tmp_file = self.check_sum_file(tmp_directory + fname)
            logger.debug(tmp_directory +
                         fname +
                         ' Checksum :: '
                         + str(chk_tmp_file))

            if unit_test == 'corrupt':
                chk_file = '0000000000'

            if chk_file == chk_tmp_file:
                logger.debug('backup file copied correctly')
                test['copy'] = True
            else:
                logger.error('backup file check sum fail')
                test['copy'] = False
                #return False

            tar.close()

            logger.debug('removing duplicate files')
            os.remove(directory + 'copy_' + fname + '.tar.' + compression_type)
            os.remove(directory + fname)

        else:
            f = open(directory + fname, 'w')
            fcopy = open('/tmp/' + fname, 'w')
            f.write(data)
            fcopy.write(data)
            f.close()
            fcopy.close()

            chk_temp = self.check_sum_file('/tmp/' + fname)
            chk_file = self.check_sum_file(directory + fname)

            if unit_test == 'corrupt':
                chk_temp = '0000000000'


            if (chk_temp == chk_file):

                logger.debug('File and copy checksums agree')
                test['checksum'] = True
            else:
                logger.error('File and copy checksums dont agree')
                test['checksum'] = False
            # Check to see if the file isthere.

        if test['checksum'] == False or test['archive'] == False or test[
            'copy'] == False:

            return False
        else:
            return True

    def check_sum_file(self, fname):
        """Generate md5sum of a file

We do it this way incase the file exceeds available memory
"""
        sha = hashlib.sha1()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha.update(chunk)

        return sha.hexdigest()

    def make_remote_backup(self, ipaddress, dbname='catamidb', **kwargs):
        """Make a back up of an offsite database"""


class ReportTools():
    """Contains tools for querying the database and reporting metrics"""

    def __init__(self):
        """Set the parameters that to report on"""

        # The name of the models.
        # TODO: Refector to query them from Django
        self.str_force_models = ['Campaign',
                                 'Deployment',
                                 'Image',
                                 'AUVDeployment',
                                 'BRUVDeployment',
                                 'DOVDeployment',
                                 'TVDeployment',
                                 'TIDeployment']

        for model in self.str_force_models:
            self.stat_fields = {model: 0}

        # List of model instances
        self.force_models = [Campaign,
                             Deployment,
                             Image,
                             AUVDeployment,
                             BRUVDeployment,
                             DOVDeployment,
                             TVDeployment,
                             TIDeployment]

    def collect_number_of_fields(self):
        """Query the number of entries inteh DB

returns logical saves data to self.stat_fields class property
"""

        i = 0
        for i in range(0, len(self.force_models)):

            self.stat_fields[self.str_force_models[i]] = len(self.force_models
            [i].objects.all())

        logger.debug(str(self.stat_fields))
        return True

    def query_table_size(self):
        """Query the size of the database table on the disk
returns the table size in bytes.

"""
        cursor = connection.cursor()

        bar_label = []
        tb_size_str = []
        tb_size = []

        query = "SELECT nspname || '.' || relname AS \"relation\", pg_size_pretty(pg_total_relation_size(C.oid)) AS \"total_size\" FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND C.relkind <> 'i' AND nspname !~ '^pg_toast' ORDER BY pg_total_relation_size(C.oid) DESC LIMIT 10;"

        cursor = connection.cursor()
        cursor.execute(query)
        for p in cursor.fetchall():
            bar_label.append(p[0])
            tb_size_str.append(p[1])


        for i in range(0, len(tb_size_str)):
            temp = tb_size_str[i].split(" ")
            tb_size.append(temp[0])
            if temp[1] == 'kB':
                tb_size[i] = int(tb_size[i]) * 1000.0
            if temp[1] == 'mB':
                tb_size[i] = db_size[i] * 1000000.0
            if temp[1] == 'gB':
                tb_size[i] = db_size[i] * 1000000000.0

        return tb_size

    def query_database_size(self, dbase='catamidb'):
        """Queries the size of the database on the disk"""
        cursor = connection.cursor()

        cursor.execute("SELECT pg_database_size('" + dbase + "')")
        self.db_size = cursor.fetchone()

        return int(self.db_size[0])

    def save(self):
        """Saves the stat fields to the database """

        try:
            collection_time=datetime.now()
            num_campaigns=self.stat_fields['Campaign']
            num_deployments=self.stat_fields['Deployment'],
            num_images=self.stat_fields['Image'],
            num_auv_deployments=self.stat_fields['AUVDeployment'],
            num_bruv_deployments=self.stat_fields['BRUVDeployment'],
            num_dov_deployments=self.stat_fields['DOVDeployment'],
            num_tv_deployments=self.stat_fields['TVDeployment'],
            num_ti_deployments=self.stat_fields['TIDeployment'],
            db_size_on_disk=self.query_database_size()

            data = DataLogger.objects.create(
                collection_time=datetime.now(),
                num_campaigns=self.stat_fields['Campaign'],
                num_deployments=self.stat_fields['Deployment'],
                num_images=self.stat_fields['Image'],
                num_auv_deployments=self.stat_fields['AUVDeployment'],
                num_bruv_deployments=self.stat_fields['BRUVDeployment'],
                num_dov_deployments=self.stat_fields['DOVDeployment'],
                num_tv_deployments=self.stat_fields['TVDeployment'],
                num_ti_deployments=self.stat_fields['TIDeployment'],
                db_size_on_disk=self.query_database_size()
            )
        except:
            traceback.print_exc(file=sys.stdout)
            raise
        data.save()

    def collect_stats(self):
        """Main method for collecting the stats"""

        try:
            logger.debug('Collecting stats')
            self.collect_number_of_fields()
            self.save()

            return True
        except:
            logger.error('Could not collect stats')
            traceback.print_exc(file=sys.stdout)
            return False

    def get_stats(self):
        """Return the stats_field dictionary"""

        self.collect_stats()

        #Query the DB


        return self.stat_fields