# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PointAnnotation.ctime'
        db.alter_column(u'annotations_pointannotation', 'ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'PointAnnotation.mtime'
        db.alter_column(u'annotations_pointannotation', 'mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True))

        # Changing field 'ImageAnnotation.ctime'
        db.alter_column(u'annotations_imageannotation', 'ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Changing field 'ImageAnnotation.mtime'
        db.alter_column(u'annotations_imageannotation', 'mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True))

    def backwards(self, orm):

        # Changing field 'PointAnnotation.ctime'
        db.alter_column(u'annotations_pointannotation', 'ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'PointAnnotation.mtime'
        db.alter_column(u'annotations_pointannotation', 'mtime', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'ImageAnnotation.ctime'
        db.alter_column(u'annotations_imageannotation', 'ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Changing field 'ImageAnnotation.mtime'
        db.alter_column(u'annotations_imageannotation', 'mtime', self.gf('django.db.models.fields.DateTimeField')(null=True))

    models = {
        u'annotations.annotationcode': {
            'Meta': {'object_name': 'AnnotationCode'},
            'caab_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'code_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'cpc_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['annotations.AnnotationCode']", 'null': 'True', 'blank': 'True'}),
            'point_colour': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        u'annotations.imageannotation': {
            'Meta': {'object_name': 'ImageAnnotation'},
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['annotations.ImageAnnotationSet']"}),
            'cover': ('django.db.models.fields.IntegerField', [], {}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Image']"}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['annotations.AnnotationCode']"}),
            'labeller': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'qualifiers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'image_annotations'", 'symmetrical': 'False', 'to': u"orm['annotations.QualifierCode']"})
        },
        u'annotations.imageannotationset': {
            'Meta': {'unique_together': "(('owner', 'name', 'collection'),)", 'object_name': 'ImageAnnotationSet'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collection.Collection']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'annotations.pointannotation': {
            'Meta': {'object_name': 'PointAnnotation'},
            'annotation_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['annotations.PointAnnotationSet']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Image']"}),
            'label': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['annotations.AnnotationCode']"}),
            'labeller': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'qualifiers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'point_annotations'", 'symmetrical': 'False', 'to': u"orm['annotations.QualifierCode']"}),
            'x': ('django.db.models.fields.FloatField', [], {}),
            'y': ('django.db.models.fields.FloatField', [], {})
        },
        u'annotations.pointannotationset': {
            'Meta': {'unique_together': "(('owner', 'name', 'collection'),)", 'object_name': 'PointAnnotationSet'},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collection.Collection']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'methodology': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'annotations.qualifiercode': {
            'Meta': {'object_name': 'QualifierCode'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'catamidb.camera': {
            'Meta': {'unique_together': "(('deployment', 'name'),)", 'object_name': 'Camera'},
            'angle': ('django.db.models.fields.IntegerField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Deployment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'catamidb.campaign': {
            'Meta': {'unique_together': "(('date_start', 'short_name'),)", 'object_name': 'Campaign'},
            'associated_publications': ('django.db.models.fields.TextField', [], {}),
            'associated_research_grant': ('django.db.models.fields.TextField', [], {}),
            'associated_researchers': ('django.db.models.fields.TextField', [], {}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'date_end': ('django.db.models.fields.DateField', [], {}),
            'date_start': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'catamidb.deployment': {
            'Meta': {'unique_together': "(('start_time_stamp', 'short_name'),)", 'object_name': 'Deployment'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Campaign']"}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'descriptive_keywords': ('django.db.models.fields.TextField', [], {}),
            'end_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'end_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {}),
            'max_depth': ('django.db.models.fields.FloatField', [], {}),
            'min_depth': ('django.db.models.fields.FloatField', [], {}),
            'mission_aim': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_position': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'start_time_stamp': ('django.db.models.fields.DateTimeField', [], {}),
            'transect_shape': ('django.contrib.gis.db.models.fields.PolygonField', [], {})
        },
        u'catamidb.image': {
            'Meta': {'unique_together': "(('pose', 'camera'),)", 'object_name': 'Image'},
            'archive_location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Camera']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pose': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Pose']"}),
            'web_location': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'catamidb.pose': {
            'Meta': {'unique_together': "(('deployment', 'date_time'),)", 'object_name': 'Pose'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'deployment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['catamidb.Deployment']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        u'collection.collection': {
            'Meta': {'unique_together': "(('owner', 'name', 'parent'),)", 'object_name': 'Collection'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creation_info': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'collections'", 'symmetrical': 'False', 'to': u"orm['catamidb.Image']"}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['collection.Collection']", 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['annotations']