# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Campaign'
        db.create_table('catamidb_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('associated_researchers', self.gf('django.db.models.fields.TextField')()),
            ('associated_publications', self.gf('django.db.models.fields.TextField')()),
            ('associated_research_grant', self.gf('django.db.models.fields.TextField')()),
            ('date_start', self.gf('django.db.models.fields.DateField')()),
            ('date_end', self.gf('django.db.models.fields.DateField')()),
            ('contact_person', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catamidb', ['Campaign'])

        # Adding unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.create_unique('catamidb_campaign', ['date_start', 'short_name'])

        # Adding model 'Deployment'
        db.create_table('catamidb_deployment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('end_position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('transect_shape', self.gf('django.contrib.gis.db.models.fields.PolygonField')()),
            ('start_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mission_aim', self.gf('django.db.models.fields.TextField')()),
            ('min_depth', self.gf('django.db.models.fields.FloatField')()),
            ('max_depth', self.gf('django.db.models.fields.FloatField')()),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Campaign'])),
            ('contact_person', self.gf('django.db.models.fields.TextField')()),
            ('descriptive_keywords', self.gf('django.db.models.fields.TextField')()),
            ('license', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catamidb', ['Deployment'])

        # Adding unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.create_unique('catamidb_deployment', ['start_time_stamp', 'short_name'])

        # Adding model 'Pose'
        db.create_table('catamidb_pose', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Deployment'])),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('position', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('depth', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('catamidb', ['Pose'])

        # Adding unique constraint on 'Pose', fields ['deployment', 'date_time']
        db.create_unique('catamidb_pose', ['deployment_id', 'date_time'])

        # Adding model 'Camera'
        db.create_table('catamidb_camera', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Deployment'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('angle', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('catamidb', ['Camera'])

        # Adding unique constraint on 'Camera', fields ['deployment', 'name']
        db.create_unique('catamidb_camera', ['deployment_id', 'name'])

        # Adding model 'Image'
        db.create_table('catamidb_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pose', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Pose'])),
            ('camera', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Camera'])),
            ('web_location', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('archive_location', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('catamidb', ['Image'])

        # Adding unique constraint on 'Image', fields ['pose', 'camera']
        db.create_unique('catamidb_image', ['pose_id', 'camera_id'])

        # Adding model 'ScientificMeasurementType'
        db.create_table('catamidb_scientificmeasurementtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('normalised_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('display_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('max_value', self.gf('django.db.models.fields.FloatField')()),
            ('min_value', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('catamidb', ['ScientificMeasurementType'])

        # Adding model 'ScientificPoseMeasurement'
        db.create_table('catamidb_scientificposemeasurement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('measurement_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.ScientificMeasurementType'])),
            ('pose', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Pose'])),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('catamidb', ['ScientificPoseMeasurement'])

        # Adding unique constraint on 'ScientificPoseMeasurement', fields ['measurement_type', 'pose']
        db.create_unique('catamidb_scientificposemeasurement', ['measurement_type_id', 'pose_id'])

        # Adding model 'ScientificImageMeasurement'
        db.create_table('catamidb_scientificimagemeasurement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('measurement_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.ScientificMeasurementType'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catamidb.Image'])),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('catamidb', ['ScientificImageMeasurement'])

        # Adding unique constraint on 'ScientificImageMeasurement', fields ['measurement_type', 'image']
        db.create_unique('catamidb_scientificimagemeasurement', ['measurement_type_id', 'image_id'])

        # Adding model 'AUVDeployment'
        db.create_table('catamidb_auvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catamidb.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('catamidb', ['AUVDeployment'])

        # Adding model 'BRUVDeployment'
        db.create_table('catamidb_bruvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catamidb.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('catamidb', ['BRUVDeployment'])

        # Adding model 'DOVDeployment'
        db.create_table('catamidb_dovdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catamidb.Deployment'], unique=True, primary_key=True)),
            ('diver_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('catamidb', ['DOVDeployment'])

        # Adding model 'TVDeployment'
        db.create_table('catamidb_tvdeployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catamidb.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('catamidb', ['TVDeployment'])

        # Adding model 'TIDeployment'
        db.create_table('catamidb_tideployment', (
            ('deployment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['catamidb.Deployment'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('catamidb', ['TIDeployment'])


    def backwards(self, orm):
        # Removing unique constraint on 'ScientificImageMeasurement', fields ['measurement_type', 'image']
        db.delete_unique('catamidb_scientificimagemeasurement', ['measurement_type_id', 'image_id'])

        # Removing unique constraint on 'ScientificPoseMeasurement', fields ['measurement_type', 'pose']
        db.delete_unique('catamidb_scientificposemeasurement', ['measurement_type_id', 'pose_id'])

        # Removing unique constraint on 'Image', fields ['pose', 'camera']
        db.delete_unique('catamidb_image', ['pose_id', 'camera_id'])

        # Removing unique constraint on 'Camera', fields ['deployment', 'name']
        db.delete_unique('catamidb_camera', ['deployment_id', 'name'])

        # Removing unique constraint on 'Pose', fields ['deployment', 'date_time']
        db.delete_unique('catamidb_pose', ['deployment_id', 'date_time'])

        # Removing unique constraint on 'Deployment', fields ['start_time_stamp', 'short_name']
        db.delete_unique('catamidb_deployment', ['start_time_stamp', 'short_name'])

        # Removing unique constraint on 'Campaign', fields ['date_start', 'short_name']
        db.delete_unique('catamidb_campaign', ['date_start', 'short_name'])

        # Deleting model 'Campaign'
        db.delete_table('catamidb_campaign')

        # Deleting model 'Deployment'
        db.delete_table('catamidb_deployment')

        # Deleting model 'Pose'
        db.delete_table('catamidb_pose')

        # Deleting model 'Camera'
        db.delete_table('catamidb_camera')

        # Deleting model 'Image'
        db.delete_table('catamidb_image')

        # Deleting model 'ScientificMeasurementType'
        db.delete_table('catamidb_scientificmeasurementtype')

        # Deleting model 'ScientificPoseMeasurement'
        db.delete_table('catamidb_scientificposemeasurement')

        # Deleting model 'ScientificImageMeasurement'
        db.delete_table('catamidb_scientificimagemeasurement')

        # Deleting model 'AUVDeployment'
        db.delete_table('catamidb_auvdeployment')

        # Deleting model 'BRUVDeployment'
        db.delete_table('catamidb_bruvdeployment')

        # Deleting model 'DOVDeployment'
        db.delete_table('catamidb_dovdeployment')

        # Deleting model 'TVDeployment'
        db.delete_table('catamidb_tvdeployment')

        # Deleting model 'TIDeployment'
        db.delete_table('catamidb_tideployment')


    models = {
        'catamidb.auvdeployment': {
            'Meta': {'object_name': 'AUVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.bruvdeployment': {
            'Meta': {'object_name': 'BRUVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.camera': {
            'Meta': {'unique_together': "(('deployment', 'name'),)", 'object_name': 'Camera'},
            'angle': ('django.db.models.fields.IntegerField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'catamidb.campaign': {
            'Meta': {'unique_together': "(('date_start', 'short_name'),)", 'object_name': 'Campaign'},
            'associated_publications': ('django.db.models.fields.TextField', [], {}),
            'associated_research_grant': ('django.db.models.fields.TextField', [], {}),
            'associated_researchers': ('django.db.models.fields.TextField', [], {}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'catamidb.deployment': {
            'Meta': {'unique_together': "(('start_time_stamp', 'short_name'),)", 'object_name': 'Deployment'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Campaign']"}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'descriptive_keywords': ('django.db.models.fields.TextField', [], {}),
            'end_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'end_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {}),
            'max_depth': ('django.db.models.fields.FloatField', [], {}),
            'min_depth': ('django.db.models.fields.FloatField', [], {}),
            'mission_aim': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'start_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'transect_shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {})
        },
        'catamidb.dovdeployment': {
            'Meta': {'object_name': 'DOVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'}),
            'diver_name': ('django.db.models.fields.TextField', [], {})
        },
        'catamidb.image': {
            'Meta': {'unique_together': "(('pose', 'camera'),)", 'object_name': 'Image'},
            'archive_location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Camera']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Pose']"}),
            'web_location': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'catamidb.pose': {
            'Meta': {'unique_together': "(('deployment', 'date_time'),)", 'object_name': 'Pose'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        'catamidb.scientificimagemeasurement': {
            'Meta': {'unique_together': "(('measurement_type', 'image'),)", 'object_name': 'ScientificImageMeasurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Image']"}),
            'measurement_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.ScientificMeasurementType']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'catamidb.scientificmeasurementtype': {
            'Meta': {'object_name': 'ScientificMeasurementType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_value': ('django.db.models.fields.FloatField', [], {}),
            'min_value': ('django.db.models.fields.FloatField', [], {}),
            'normalised_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'catamidb.scientificposemeasurement': {
            'Meta': {'unique_together': "(('measurement_type', 'pose'),)", 'object_name': 'ScientificPoseMeasurement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.ScientificMeasurementType']"}),
            'pose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catamidb.Pose']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'catamidb.tideployment': {
            'Meta': {'object_name': 'TIDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        },
        'catamidb.tvdeployment': {
            'Meta': {'object_name': 'TVDeployment', '_ormbases': ['catamidb.Deployment']},
            'deployment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['catamidb.Deployment']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['catamidb']