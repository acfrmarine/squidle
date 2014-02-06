from tastypie import fields
from tastypie.resources import ModelResource
from .models import Collection

from tastypie.authentication import (Authentication,
                                     SessionAuthentication,
                                     MultiAuthentication,
                                     ApiKeyAuthentication)
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
    get_users_with_perms, get_groups_with_perms)

from jsonapi.api import UserResource
from jsonapi.security import get_real_user_object


class CollectionAuthorization(Authorization):
    """Implements authorization for collections.

    Restricts access to reading, deleting and updating of details,
    and to only reading of lists.
    """

    def read_list(self, object_list, bundle):
        """Restrict the list to only user visible collections."""
        user = get_real_user_object(bundle.request.user)
        user_objects = get_objects_for_user(user, [
            'collection.view_collection'], object_list)

        return user_objects

    def read_detail(self, object_list, bundle):
        """Check user has permission to view this collection."""
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('collection.view_collection', bundle.obj):
            return True

        raise Unauthorized()

    def delete_list(self, object_list, bundle):
        """Currently do not permit deletion of any collections.
        """
        raise Unauthorized(
            "You do not have permission to delete this collection.")

    def delete_detail(self, object_list, bundle):
        """Currently do not permit deletion of any collections.
        """
        raise Unauthorized(
            "You do not have permission to delete this collection.")

    def update_detail(self, object_list, bundle):
        """Restrict access to updating a collection.
        """
        # get the original object (this is needed in case we are locking it)
        # bundle.obj is the modified value
        # the original can be found in object_list
        original = object_list.get(id=bundle.obj.id)
        user = get_real_user_object(bundle.request.user)
        if user.has_perm('collection.change_collection', original):
            # the user has permission to edit - but not all edits are permitted
            # it is a fairly complex setup - locked prevents certain things,
            # but not others etc. this isn't so much an authorisation issue but
            # a model issue however
            return True
        else:
            raise Unauthorized(
                "This collection is locked and cannot be unlocked or modified."
            )


class CollectionResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    parent = fields.ForeignKey('collection.api.CollectionResource', 'parent',
        null=True)

    class Meta:
        queryset = Collection.objects.all()
        resource_name = "collection"
        authentication = MultiAuthentication(SessionAuthentication(),
                                             ApiKeyAuthentication(),
                                             Authentication())
        authorization = CollectionAuthorization()
        detail_allowed_methods = ['get', 'put']
        list_allowed_methods = ['get']
        filtering = {
            'is_public': 'exact',
            'owner': 'exact',
            'id': 'exact',
            'parent': ['exact', 'isnull'],
        }
        ordering = ['name']

    def dehydrate(self, bundle):
        """Add an image_count field to CollectionResource."""
        bundle.data['image_count'] = Collection.objects.get(pk=bundle.data[
            'id']).images.count()
        if bundle.obj.parent:
            bundle.data['parent_id'] = bundle.obj.parent.pk
        else:
            bundle.data['parent_id'] = None
        return bundle
