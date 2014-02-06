"""Extends the management commands to include checkdb

Checks the data is still conforming to the model bounds
"""

from django.core.management.base import BaseCommand
from django.core.management.base import NoArgsCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from optparse import make_option
from lib.progress import with_progress_meter


def model_name(model):
    """Grab the name of the model"""
    return '%s.%s' % (model._meta.app_label, model._meta.object_name)


class Command(BaseCommand):
    """Extend the commands available to ./manage.py"""
    
    args = '[-e|--exclude app_name.ModelName]'
    help = (
        'Checks constraints in the database and reports violations on stdout')

    option_list = NoArgsCommand.option_list + (make_option('-e', '--exclude',
        action='append', type='string', dest='exclude'),)

    def handle(self, *args, **options):

        exclude = options.get('exclude', None) or []

        failed_instance_count = 0
        failed_model_count = 0
        for app in models.get_apps():
            for model in models.get_models(app):
                if model_name(model) in exclude:
                    self.stdout.write('Skipping model ' + str(model_name(model
                        )))
                    continue
                fail_count = self.check_model( model)
                if fail_count > 0:
                    failed_model_count += 1
                    failed_instance_count += fail_count
        self.stderr.write('Detected ' + str(failed_instance_count) +
            ' errors in ' + str(failed_model_count) + ' models')

    def check_model(self, model):
        """Check to see if models are proxy or not"""
        meta = model._meta
        if meta.proxy:
            self.stdout.write(
                'WARNING: proxy models not currently supported; ignored')
            return

        # Define all the checks we can do; they return True if they are ok,
        # False if not (and print a message to stdout)
        def check_foreign_key(model, field):
            """Check that foreign keys refer to models that exist"""
            foreign_model = field.related.parent_model

            def check_instance(instance):
                """Check that the model attributes exist on the DB"""
                try:
                    # name: name of the attribute containing the model instance
                    # (e.g. 'user') attname: name of the attribute containing
                    # the id (e.g. 'user_id')
                    getattr(instance, field.name)
                    return True
                except ObjectDoesNotExist:
                    self.stdout(str(model_name(model)) + ' with pk ' + str(
                        instance.pk) + ' refers via field ' + field.name +
                        ' to nonexistent ' + model_name(foreign_model) +
                        ' with pk ' + getattr(instance, field.attname))
            return check_instance

        # Make a list of checks to run on each model instance
        checks = []
        for field in (meta.local_fields + meta.local_many_to_many + meta.
            virtual_fields):
            if isinstance(field, models.ForeignKey):
                checks.append(check_foreign_key(model, field))

        # Run all checks
        fail_count = 0
        if checks:
            for instance in with_progress_meter(model.objects.all(), model.
                objects.count(), 'Checking model %s ...' % model_name(model)):
                for check in checks:
                    if not check(instance):
                        fail_count += 1
        return fail_count
