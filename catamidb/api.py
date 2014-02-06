from shutil import copy
from django.contrib.auth.models import User
import guardian
from guardian.shortcuts import (get_objects_for_user, get_perms_for_model,
                                get_users_with_perms, get_groups_with_perms)
from tastypie import fields
from tastypie.authentication import (MultiAuthentication,
                                     SessionAuthentication,
                                     ApiKeyAuthentication,
                                     Authentication,
                                     BasicAuthentication)
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, Resource
from .models import *
from .settings import WEB_THUMBNAIL_SIZE
from restthumbnails.helpers import get_thumbnail_proxy
from annotations import models as annotation_models




# ==============================
# Auth configuration for the API
# ==============================

#need this because guardian lookups require the actual django user object
def get_real_user_object(tastypie_user_object):
    # blank username is anonymous
    if tastypie_user_object.is_anonymous():
        user = guardian.utils.get_anonymous_user()
    else:  # if not anonymous, get the real user object from django
        user = User.objects.get(id=tastypie_user_object.id)

    #send it off
    return user


# Used to allow authent of anonymous users for GET requests
class AnonymousGetAuthentication(SessionAuthentication):
    def is_authenticated(self, request, **kwargs):
        # let anonymous users in for GET requests - Authorisation logic will
        # stop them from accessing things not allowed to access
        if request.user.is_anonymous() and request.method == "GET":
            return True

        return super(AnonymousGetAuthentication, self).is_authenticated(
            request, **kwargs)

# ========================
# API configuration
# ========================

class CampaignResource(ModelResource):
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = "campaign"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        allowed_methods = ['get']

class DeploymentResource(ModelResource):
    campaign = fields.ForeignKey(CampaignResource, 'campaign')

    class Meta:
        queryset = Deployment.objects.prefetch_related("campaign").all()
        resource_name = "deployment"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'campaign': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']
        ordering = ['short_name']


class PoseResource(ModelResource):
    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    images = fields.ToManyField('catamidb.api.ImageResource', 'image', related_name='pose', null=True)
    measurements = fields.ToManyField(
        'catamidb.api.ScientificPoseMeasurementResource',
        'scientificposemeasurement_set')

    class Meta:
        queryset = Pose.objects.all()
        resource_name = "pose"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'depth': ['range', 'gt', 'lt', 'gte', 'lte'],
            'images': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']

    def dehydrate_measurements(self, bundle):
        # change to view a small subset of the info
        # the rest isn't really needed in this resource
        outlist = []
        for m in bundle.obj.scientificposemeasurement_set.all():
            outitem = {}
            outitem['value'] = m.value
            outitem['units'] = m.measurement_type.units
            outitem['name'] = m.measurement_type.display_name
            outlist.append(outitem)

        return outlist

    def dehydrate_images(self, bundle):
        """Dehydrate images within a pose.

        This override is to remove the pose uri field as it
        is redundant when included as part of a pose.
        """
        outlist = []
        for image in bundle.obj.image_set.all():
            outimage = {}
            file_name = image.web_location
            outimage['web_location'] = '/images/{0}'.format(file_name)
            outimage['thumbnail_location'] = get_thumbnail_proxy(
                    file_name,
                    "{0}x{1}".format(*WEB_THUMBNAIL_SIZE),
                    'scale',
                    '.jpg'
                ).url
            outimage['id'] = image.id
            #outimage['resource_uri'] = self.fields['images'].related_resource.get_resource_uri(image)

            outlist.append(outimage)

        return outlist

class ImageResource(ModelResource):
    pose = fields.ForeignKey(PoseResource, 'pose')
    measurements = fields.ToManyField(
        'catamidb.api.ScientificImageMeasurementResource',
        'scientificimagemeasurement_set')
    collection = fields.ToManyField('collection.api.CollectionResource',
                                    'collections')

    class Meta:
        queryset = Image.objects.prefetch_related("pose").all()
        resource_name = "image"
        excludes = ['archive_location', 'collections']
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'pose': ALL_WITH_RELATIONS,
            'collection': ALL,
            'id': ALL_WITH_RELATIONS,

        }
        allowed_methods = ['get']
        ordering = ['id']

    def dehydrate_measurements(self, bundle):
        # change to view a small subset of the info
        # the rest isn't really needed in this resource
        outlist = []

        for m in bundle.obj.scientificimagemeasurement_set.all():
            outitem = {}
            outitem['value'] = m.value
            outitem['units'] = m.measurement_type.units
            outitem['name'] = m.measurement_type.display_name
            outlist.append(outitem)

        return outlist

    def dehydrate(self, bundle):
        file_name = bundle.data['web_location']
        # if annotation set filter used, return annotation_count to results
        set_id = bundle.request.GET.get("annotation_set")
        exlcude_label = bundle.request.GET.get("annotation_label_ne") # exclude single label
        filter_label = bundle.request.GET.get("annotation_label_eq") # filter by single label
        if set_id:
            image_id = bundle.data["id"]
            annotation_points = annotation_models.PointAnnotation.objects.filter(annotation_set=set_id, image=image_id)
            bundle.data['annotation_count'] = annotation_points.count()
            if exlcude_label:
                bundle.data['annotation_labelled_count'] = annotation_points.exclude(label=exlcude_label).count()
            elif filter_label:
                bundle.data['annotation_labelled_count'] = annotation_points.filter(label=filter_label).count()

        bundle.data['thumbnail_location'] = get_thumbnail_proxy(
            file_name,
            "{0}x{1}".format(*WEB_THUMBNAIL_SIZE),
            'scale',
            '.jpg'
        ).url
        bundle.data['web_location'] = '/images/{0}'.format(file_name)
        del bundle.data['collection']
        return bundle

    def get_object_list(self, request):
        images = super(ImageResource, self).get_object_list(request)

        #get the ranges to query on
        temperature__gte = request.GET.get("temperature__gte")
        temperature__lte = request.GET.get("temperature__lte")

        salinity__gte = request.GET.get("salinity__gte")
        salinity__lte = request.GET.get("salinity__lte")

        altitude__gte = request.GET.get("altitude__gte")
        altitude__lte = request.GET.get("altitude__lte")

        # get the measurement types we want to query
        measurement_types = ScientificMeasurementType.objects.all()
        temperature = measurement_types.get(normalised_name="temperature")
        salinity = measurement_types.get(normalised_name="salinity")
        altitude = measurement_types.get(normalised_name="altitude")

        #filter temperature
        if temperature__lte is not None and temperature__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=temperature, pose__scientificposemeasurement__value__range=(temperature__gte, temperature__lte))

        #then filter out salinity - chain
        if salinity__lte is not None and salinity__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=salinity, pose__scientificposemeasurement__value__range=(salinity__gte, salinity__lte))

        #then filter out altitude - chain
        if altitude__lte is not None and altitude__gte is not None:
            images = images.filter(pose__scientificposemeasurement__measurement_type=altitude, pose__scientificposemeasurement__value__range=(altitude__gte, altitude__lte))

        return images

class ScientificMeasurementTypeResource(ModelResource):
    class Meta:
        queryset = ScientificMeasurementType.objects.all()
        resource_name = "scientificmeasurementtype"
        allowed_methods = ['get']
        filtering = {
            'normalised_name': ALL,
        }

class SimplePoseResource(ModelResource):
    """
        SimplePoseResource has very limited relations. This is used for
        performance purposes. i.e. Directly querying this resource should
        be fast-ish...
    """

    deployment = fields.ForeignKey(DeploymentResource, 'deployment')
    #images = fields.ToManyField('catamidb.api.ImageResource', 'image_set',full=True)
    #measurements = fields.ToManyField(
    #    'catamidb.api.ScientificPoseMeasurementResource',
    #    'scientificposemeasurement_set')

    class Meta:
        queryset = Pose.objects.prefetch_related("deployment").all()
        resource_name = "simplepose"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'deployment': ALL_WITH_RELATIONS,
            'depth': ['range', 'gt', 'lt'],
            'id': ALL_WITH_RELATIONS,
            }
        allowed_methods = ['get']

    #this gets called just before sending response
    def alter_list_data_to_serialize(self, request, data):

        #if flot is asking for the data, we need to package it up a bit
        if request.GET.get("output") == "flot":
            return self.package_series_for_flot_charts(data)

        return data

    #flot takes a two dimensional array of data, so we need to package the
    #series up in this manner
    def package_series_for_flot_charts(self, data):
        data_table = []

        #scale factors for reducing the data
        list_length = len(data['objects'])
        scale_factor = 4

        #for index, bundle in enumerate(data['objects']):
        #    data_table.append([index, bundle.obj.value])
        for i in range(0, list_length, scale_factor):
            data_table.append([i, data['objects'][i].data['depth']])

        return {'data': data_table}

class ScientificPoseMeasurementResource(ModelResource):

    #this pose is related to the SimplePoseResource for performance pruposes
    pose = fields.ToOneField(SimplePoseResource, 'pose')
    mtype = fields.ToOneField(ScientificMeasurementTypeResource, "measurement_type")

    class Meta:
        queryset = ScientificPoseMeasurement.objects.prefetch_related("pose")\
            .prefetch_related("measurement_type").all()
        resource_name = "scientificposemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'pose': ALL_WITH_RELATIONS,
            'mtype': ALL_WITH_RELATIONS,
        }
        allowed_methods = ['get']

    def alter_list_data_to_serialize(self, request, data):

        #if flot is asking for the data, we need to package it up a bit
        if request.GET.get("output") == "flot":
            return self.package_series_for_flot_charts(data)

        return data

    #flot takes a two dimensional array of data, so we need to package the
    #series up in this manner
    def package_series_for_flot_charts(self, data):
        data_table = []

        #scale factors for reducing the data
        list_length = len(data['objects'])
        scale_factor = 4

        #for index, bundle in enumerate(data['objects']):
        #    data_table.append([index, bundle.obj.value])
        for i in range(0, list_length, scale_factor):
            data_table.append([i, data['objects'][i].data['value']])

        return {'data': data_table}

class ScientificImageMeasurementResource(ModelResource):
    image = fields.ToOneField('catamidb.api.ImageResource', 'image')

    class Meta:
        queryset = ScientificImageMeasurement.objects.all()
        resource_name = "scientificimagemeasurement"
        authentication = MultiAuthentication(AnonymousGetAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'image': 'exact',
        }
        allowed_methods = ['get']

