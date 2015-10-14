from tastypie import fields, http
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.resources import convert_post_to_patch
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication, SessionAuthentication, MultiAuthentication, ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound, BadRequest, Unauthorized

from django.views.decorators.csrf import csrf_exempt

from tastypie.utils import is_valid_jsonp_callback_value, dict_strip_unicode_keys, trailing_slash

import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms, assign)

import django
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from collection.models import Collection
from catamidb.models import Image
from annotations.models import PointAnnotationSet, PointAnnotation, AnnotationCode

from . import models 
from catamidb.api import AnonymousGetAuthentication, get_real_user_object

import logging

logger = logging.getLogger(__name__)

class AnnotationCodeResource(ModelResource):
    parent = fields.ForeignKey('annotations.api.AnnotationCodeResource', 'parent', null=True)
    
    class Meta:
        queryset = models.AnnotationCode.objects.all()
        resource_name = "annotation_code"
        # use defaults - no special permissions are needed here
        # for authorization and authentication
        filtering = {
            'parent': ALL_WITH_RELATIONS,
            'code_name': ALL,
            'id': ALL,
        }
        allowed_methods = ['get']
        ordering = ['code_name', 'caab_code', 'cpc_code']

    def dehydrate(self, bundle):
        """Add a parent_id field to AnnotationCodeResource."""
        if bundle.obj.parent:
            bundle.data['parent_id'] = bundle.obj.parent.pk
        else:
            bundle.data['parent_id'] = None
        return bundle
    

class QualifierCodeResource(ModelResource):
    
    class Meta:
        queryset = models.QualifierCode.objects.all()
        resource_name = "qualifier_code"
        # use defaults - no special permissions are needed here
        # for authorization and authentication
        filtering = {
            'modifier_name': ALL,
        }
        allowed_methods = ['get']
        ordering = ['modifier_name']

class PointAnnotationSetAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        ## get the objects the user has permission to see
        #user_objects = get_objects_for_user(
        #        user,
        #        ['annotations.view_pointannotationset'],
        #        object_list
        #    )
        user_objects = object_list # !!! remove this line and uncomment above to filter based on permissions

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        return True # !!! remove this line to filter based on permissions
        if user.has_perm('annotations.view_pointannotationset', bundle.obj):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # the object may not be fully hydrated yet... this is called
        # twice - once quite early, the other time just before saving
        # the first time we lack enough information to do this properly
        # but the second time we don't - so skip through the first time
        if bundle.obj.collection_id is None:
            return True

        # check if they are allowed to create point annotation sets
        if user.has_perm('collection.view_collection', bundle.obj.collection):
            return True

        raise Unauthorized("You are not allowed to create point sets on the parent collection.")

    def create_list(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check if they are allowed to create point annotation sets
        if user.has_perm('annotations.create_pointannotationset', bundle.obj):
            return True

        raise Unauthorized("You are not allowed to create point sets.")

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        user = get_real_user_object(bundle.request.user)
        if user.has_perm('annotations.update_pointannotationset', bundle.obj.annotation_set):
            return True
        raise Unauthorized("Sorry, no deletes.")

class PointAnnotationSetResource(ModelResource):
    collection = fields.ForeignKey('collection.api.CollectionResource', 'collection')
    owner = fields.ForeignKey('jsonapi.api.UserResource', 'owner')
    
    class Meta:
        queryset = models.PointAnnotationSet.objects.all()
        resource_name = "point_annotation_set"
        filtering = {
            'collection': ALL_WITH_RELATIONS,
            'name': ALL,
            'id': 'exact',
        }
        allowed_methods = ['get', 'post', 'delete']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                SessionAuthentication(),
                ApiKeyAuthentication())
        authorization = PointAnnotationSetAuthorization()
        ordering = ['name']

    # an override that is needed to be able to get related objects.
    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        self.authorized_create_detail(self.get_object_list(bundle.request), bundle)
        bundle = self.full_hydrate(bundle)
        bundle = self.save(bundle)

        user = get_real_user_object(bundle.request.user)

        assign('annotations.view_pointannotationset', user, bundle.obj)
        assign('annotations.update_pointannotationset', user, bundle.obj)
        return bundle

class PointAnnotationAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # get real user object
        user = get_real_user_object(bundle.request.user)

        # get the objects the user has permission to see
        # may be able to cache the lookup based on if have seen that
        # annotationset before
        #user_objects = []
        #for o in object_list:
        #    if user.has_perm('annotations.view_pointannotationset', o.annotation_set):
        #        user_objects.append(o)
        user_objects = object_list # !!! remove this line and uncomment above to filter based on permissions

        # send em off
        return user_objects

    def read_detail(self, object_list, bundle):
        # get real user
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        return True  # !!! remove this line to filter based on permissions
        if user.has_perm('annotations.view_pointannotationset', bundle.obj.annotation_set):
            return True

        # raise hell! - https://github.com/toastdriven/django-
        # tastypie/issues/826
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        # get real user
        # raise Unauthorized("Sorry, no creates.")
        return True

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        user = get_real_user_object(bundle.request.user)

        # check the user has permission to view this object
        if user.has_perm('annotations.update_pointannotationset', bundle.obj.annotation_set):
            return True
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        user = get_real_user_object(bundle.request.user)
        if user.has_perm('annotations.update_pointannotationset', bundle.obj.annotation_set):
            # only allow deletes if correct user and correct methodology
            if bundle.obj.annotation_set.methodology == 4:
                return True
        raise Unauthorized("Sorry, no deletes.")


class PointAnnotationResource(ModelResource):
    image = fields.ForeignKey('catamidb.api.ImageResource', 'image')
    label = fields.ForeignKey(AnnotationCodeResource, 'label')
    qualifiers = fields.ToManyField(QualifierCodeResource, 'qualifiers')
    #labeller = fields.ForeignKey( # User
    annotation_set = fields.ForeignKey(PointAnnotationSetResource, 'annotation_set')

    class Meta:
        queryset = models.PointAnnotation.objects.all()
        resource_name = "point_annotation"
        filtering = {
            'image': ALL_WITH_RELATIONS,
            'label': ALL_WITH_RELATIONS,
            'qualifier': ALL_WITH_RELATIONS,
            'annotation_set': ALL_WITH_RELATIONS,
            'level': ALL,
        }
        allowed_methods = ['get', 'patch', 'post', 'delete']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                SessionAuthentication(),
                ApiKeyAuthentication())
        authorization = PointAnnotationAuthorization()
        always_return_data = True
        ordering = ['x', 'y']


    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        # bundle.obj = self._meta.object_class()

        print "\n\n\nCREATE NEW ANNOTATION POINT!!!\n\n\n"

        annotation_set = PointAnnotationSet.objects.get(id=bundle.data['annotation_set_id'])

        if annotation_set.methodology == 4:
            image = Image.objects.get(id=bundle.data['image_id'])
            labeller = get_real_user_object(bundle.request.user)
            label = AnnotationCode.objects.get(id=bundle.data['label_id'])

            setattr(bundle.obj, "annotation_set", annotation_set)
            setattr(bundle.obj, "image", image)
            setattr(bundle.obj, "labeller", labeller)
            setattr(bundle.obj, "label", label)
            setattr(bundle.obj, "level", bundle.data['level'])
            setattr(bundle.obj, "x", bundle.data['x'])
            setattr(bundle.obj, "y", bundle.data['y'])

            bundle.obj.save()


        print "\n\n\nDONE!!!\n\n\n"

        return bundle

    def obj_get_list(self, bundle, **kwargs):
        """Overrides the given method from ModelResource.

        This is to enable creation of the annotation points on
        first retrieval.

        Must have filter for image & annotation set. And nothing else.
        """

        filters = {}
        if hasattr(bundle.request, 'GET'):
            filters = bundle.request.GET.copy()

        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        # check if we match the exact filters required...
        # if extras, or either missing/repeated then ignore
        # and act as normal
        extras = False
        image_restriction = False
        set_restriction = False

        image_id = 0
        set_id = 0
        # check that the only two restrictions are this...
        for k, v in applicable_filters.iteritems():
            if not set_restriction and k == 'annotation_set__exact':
                set_restriction = True
                set_id = v
            elif not image_restriction and k == 'image__exact':
                image_restriction = True
                image_id = v
            else:
                extras = True

        if image_restriction and set_restriction and not extras:
            # get the set we are working with
            annotation_set = models.PointAnnotationSet.objects.get(id=set_id)

            # check if image in collection that annotationset links to
            image_in_collection = annotation_set.collection.images.filter(
                    id=image_id
                ).exists()

            # we want to ignore creating annotations for images not in the set
            if image_in_collection:
                # now check to see how many things there be
                # if count != n, then make them!
                # or do other error things if n != 0

                objects = self.apply_filters(bundle.request, applicable_filters)

                # if there are none then create them all
                # potentially should check for cases where count != expected
                if objects.count() == 0:
                    # create them all!
                    image = Image.objects.get(id=image_id)
                    user = get_real_user_object(bundle.request.user)
                    models.PointAnnotation.objects.create_annotations(
                            annotation_set,
                            image,
                            user
                        )

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)

            # prob at this point do it...

            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type.")



    def patch_list(self, request, **kwargs):
        """Override of the default to make the allowed methods map better.

        Mainly makes delete depend on delete (already happend).
        Makes creation depend on post, full update/create with URI depend
        on put and update existing depend on patch - which isn't a method at
        all.
        """
        request = convert_post_to_patch(request)
        if django.VERSION >= (1, 4):
            body = request.body
        else:
            body = request.raw_post_data
        deserialized = self.deserialize(request, body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        collection_name = self._meta.collection_name
        deleted_collection_name = 'deleted_%s' % collection_name
        if collection_name not in deserialized:
            raise BadRequest("Invalid data sent: missing '%s'" % collection_name)

        #if len(deserialized[collection_name]) and 'put' not in self._meta.detail_allowed_methods:
        #    raise ImmediateHttpResponse(response=http.HttpMethodNotAllowed())

        bundles_seen = []

        for data in deserialized[collection_name]:
            # If there's a resource_uri then this is either an
            # update-in-place or a create-via-PUT.
            if "resource_uri" in data:
                uri = data.pop('resource_uri')

                try:
                    obj = self.get_via_uri(uri, request=request)

                    # The object does exist, so this is an update-in-place.
                    if 'patch' not in self._meta.detail_allowed_methods:
                        raise ImmediateHttpResponse(response=http.HttpMethodNotAllowed())
                    bundle = self.build_bundle(obj=obj, request=request)
                    bundle = self.full_dehydrate(bundle, for_list=True)
                    bundle = self.alter_detail_data_to_serialize(request, bundle)
                    self.update_in_place(request, bundle, data)
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    # The object referenced by resource_uri doesn't exist,
                    # so this is a create-by-PUT equivalent.
                    if 'put' not in self._meta.detail_allowed_methods:
                        raise ImmediateHttpResponse(response=http.HttpMethodNotAllowed())
                    data = self.alter_deserialized_detail_data(request, data)
                    bundle = self.build_bundle(data=dict_strip_unicode_keys(data), request=request)
                    self.obj_create(bundle=bundle)
            else:
                # There's no resource URI, so this is a create call just
                # like a POST to the list resource.
                if 'post' not in self._meta.detail_allowed_methods:
                    raise ImmediateHttpResponse(response=http.HttpMethodNotAllowed())

                data = self.alter_deserialized_detail_data(request, data)
                bundle = self.build_bundle(data=dict_strip_unicode_keys(data), request=request)
                self.obj_create(bundle=bundle)

            bundles_seen.append(bundle)

        deleted_collection = deserialized.get(deleted_collection_name, [])

        if deleted_collection:
            if 'delete' not in self._meta.detail_allowed_methods:
                raise ImmediateHttpResponse(response=http.HttpMethodNotAllowed())

            for uri in deleted_collection:
                obj = self.get_via_uri(uri, request=request)
                bundle = self.build_bundle(obj=obj, request=request)
                self.obj_delete(bundle=bundle)

        if not self._meta.always_return_data:
            return http.HttpAccepted()
        else:
            to_be_serialized = {}
            to_be_serialized['objects'] = [self.full_dehydrate(bundle, for_list=True) for bundle in bundles_seen]
            to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
            return self.create_response(request, to_be_serialized, response_class=http.HttpAccepted)

    def update_in_place(self, request, original_bundle, new_data):
        """
        Update the object in original_bundle in-place using new_data.
        """
        updated = dict_strip_unicode_keys(new_data)

        usable = {}
        permitted_values = ['label', 'level', 'qualifiers']

        for pv in permitted_values:
            if pv in updated:
                usable[pv] = updated[pv]

        user = get_real_user_object(request.user)

        # maybe should be pk, or uri not user object...
        usable['labeller'] = user

        original_bundle.data.update(**usable)

        # Now we've got a bundle with the new data sitting in it and we're
        # we're basically in the same spot as a PUT request. SO the rest of this
        # function is cribbed from put_detail.
        self.alter_deserialized_detail_data(request, original_bundle.data)
        kwargs = {
            self._meta.detail_uri_name: self.get_bundle_detail_data(original_bundle),
            'request': request,
        }
        return self.obj_update(bundle=original_bundle, **kwargs)


    def dehydrate(self, bundle):
        bundle.data['label_name'] = bundle.obj.label.code_name
        bundle.data['label_colour'] = bundle.obj.label.point_colour
        bundle.data['label_cpc_code'] = bundle.obj.label.cpc_code
        outlist = []
        for m in bundle.obj.qualifiers.all():
            outlist.append(m.modifier_name)

        bundle.data['qualifier_names'] = outlist
        return bundle
