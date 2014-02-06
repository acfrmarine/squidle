"""Unit tests for the administratorbot
"""

from django.test import TestCase
from model_mommy import mommy
import dbadmintool.administratorbot as administratorbot
from django.contrib.gis.geos import Point, Polygon

from django.test.client import RequestFactory


class DatabaseTest(TestCase):
    """Tests for checking the database administratorbot"""

    #fixtures = ['data.json', ]

    def setUp(self):
        """Set up the defaults for the test"""
        self.bender = administratorbot.Robot()
        self.april = administratorbot.ReportTools()

    def test_check_database_connection(self):
        """Test that administratorbot returns True if open connection and

        False if no connection is found
        """

        # The unt test database is called default.see if we can get a
        # connection
        self.assertTrue(self.bender.check_database_connection(
            dbname='default'))

        # Now check that we get a logical return if we cannot connect
        self.assertFalse(self.bender.check_database_connection(
            dbname='nodatabase'))

    def test_make_local_backup(self):
        self.assertTrue(self.bender.make_local_backup())
        self.assertTrue(self.bender.make_local_backup(do_zip=False))
        self.assertFalse(self.bender.make_local_backup(do_zip=False,
                                                       unit_test='corrupt'))
        self.assertFalse(self.bender.make_local_backup(unit_test='corrupt'))

    def test_collect_db_stats(self):
        # Load some data to count
        self.assertTrue(self.april.collect_number_of_fields())
        self.assertTrue(self.april.collect_stats())
        self.assertTrue(isinstance(self.april.query_database_size(), int))
        self.assertTrue(isinstance(self.april.query_table_size(), list))

        #def test_db_stats_view(self):
        #response = self.client.get("/report/")

