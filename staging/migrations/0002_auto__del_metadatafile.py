# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'MetadataFile'
        db.delete_table('staging_metadatafile')


    def backwards(self, orm):
        # Adding model 'MetadataFile'
        db.create_table('staging_metadatafile', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('metadata_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('staging', ['MetadataFile'])


    models = {

    }

    complete_apps = ['staging']