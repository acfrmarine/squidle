# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feedback'
        db.create_table('feedbacks_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('brief_description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('full_description', self.gf('django.db.models.fields.TextField')()),
            ('request_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('feedbacks', ['Feedback'])


    def backwards(self, orm):
        # Deleting model 'Feedback'
        db.delete_table('feedbacks_feedback')


    models = {
        'feedbacks.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'brief_description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'request_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['feedbacks']
