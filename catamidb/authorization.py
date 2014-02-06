
import logging
from django.contrib.auth.models import Group
from django.dispatch import receiver
import guardian
from guardian.shortcuts import assign, assign
from userena.signals import signup_complete

logger = logging.getLogger(__name__)


# this is to be called from webinterface urls.py
def on_startup_configuration():

    # I did not use a fixture for this because the anonymous user is created by
    # django-guardian at syncdb time. Trying to load fixtures on top of already
    # configured data seems messy. Doing it here instead.

    # create a public group - this is so we can assign public information to it
    public_group, created = Group.objects.get_or_create(name='Public')
    logger.debug("Created initial Public group.")

    # add the anonymous user to this group
    guardian.utils.get_anonymous_user().groups.add(public_group)
    logger.debug("Assigned AnonymousUser to the Public group.")


#this is for listening to when userena is finished registering users
@receiver(signup_complete)
def on_signup_assign_to_public_group(sender, **kwargs):

    # add new users to the Public group - so they can see stuff made public
    public_group, created = Group.objects.get_or_create(name='Public')
    kwargs.get('user').groups.add(public_group)

