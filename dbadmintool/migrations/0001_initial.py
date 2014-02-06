# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataLogger'
        db.create_table('dbadmintool_datalogger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('num_campaigns', self.gf('django.db.models.fields.IntegerField')()),
            ('num_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('num_images', self.gf('django.db.models.fields.IntegerField')()),
            ('num_auv_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('num_bruv_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('num_dov_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('num_tv_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('num_ti_deployments', self.gf('django.db.models.fields.IntegerField')()),
            ('db_size_on_disk', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dbadmintool', ['DataLogger'])


    def backwards(self, orm):
        # Deleting model 'DataLogger'
        db.delete_table('dbadmintool_datalogger')


    models = {
        'dbadmintool.datalogger': {
            'Meta': {'object_name': 'DataLogger'},
            'collection_time': ('django.db.models.fields.DateTimeField', [], {}),
            'db_size_on_disk': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_auv_deployments': ('django.db.models.fields.IntegerField', [], {}),
            'num_bruv_deployments': ('django.db.models.fields.IntegerField', [], {}),
            'num_campaigns': ('django.db.models.fields.IntegerField', [], {}),
            'num_deployments': ('django.db.models.fields.IntegerField', [], {}),
            'num_dov_deployments': ('django.db.models.fields.IntegerField', [], {}),
            'num_images': ('django.db.models.fields.IntegerField', [], {}),
            'num_ti_deployments': ('django.db.models.fields.IntegerField', [], {}),
            'num_tv_deployments': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['dbadmintool']