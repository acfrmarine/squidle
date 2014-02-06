from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

from django.contrib.auth.models import User

from django.db.models import Q

import guardian
from guardian.shortcuts import get_objects_for_user, \
    get_perms_for_model, get_users_with_perms, get_groups_with_perms


def get_real_user_object(tastypie_user_object):
    # blank username is anonymous
    if tastypie_user_object.is_anonymous():
        user = guardian.utils.get_anonymous_user()
    else: # if not anonymous, get the real user object from django
        user = User.objects.get(id=tastypie_user_object.id)

    #send it off
    return user


