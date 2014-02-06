from datetime import datetime
from dateutil.tz import tzutc
from django.contrib.gis.db import models

from django.contrib.auth.models import User
from catamidb.models import Image, Deployment, ScientificMeasurementType
from random import sample
import logging
from collection import authorization
from django.db.utils import IntegrityError
from django.db.models import Count
#from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import *

import os

logger = logging.getLogger(__name__)


class CollectionManager(models.Manager):
    """Manager for collection objects.

    Has methods to assist in creation collections and worksets.
    """

    #def collection_from_deployment(self, user, deployment):
    #    """Create a collection using all images in a deployment.
    #
    #    :returns: the created collection.
    #    """
    #
    #    # create and prefill the collection as much as possible
    #    collection = Collection()
    #    collection.name = deployment.short_name
    #    collection.owner = user
    #    collection.creation_date = datetime.now(tz=tzutc())
    #    collection.modified_date = datetime.now(tz=tzutc())
    #    collection.is_locked = True
    #    collection.creation_info = "Deployments: {0}".format(deployment.short_name)
    #
    #    # save the collection so we can associate images with it
    #    collection.save()
    #
    #    #apply permissions
    #    authorization.apply_collection_permissions(user, collection)
    #
    #    # now add all the images
    #    images = Image.objects.filter(pose__deployment=deployment)
    #    collection.images.add(*images)
    #
    #    return collection
    #
    #def collection_from_deployments_with_name(self, user, collection_name,
    #    deployment_id_list_string):
    #    """Create a collection using all images in a deployment.
    #
    #    :returns: the created collection.
    #    """
    #    try:
    #
    #        # check user is logged in
    #        if user.is_anonymous() or  not user.is_authenticated :
    #            raise CollectionError("You need to be logged in to create a Project...")
    #
    #        #print "passed permission test"
    #
    #
    #        # create and prefill the collection as much as possible
    #        collection = Collection()
    #        collection.name = collection_name
    #        collection.owner = user
    #        collection.creation_date = datetime.now(tz=tzutc())
    #        collection.modified_date = datetime.now(tz=tzutc())
    #        collection.is_public = False
    #        collection.is_locked = True
    #        collection.creation_info = "Deployments: {0}".format(deployment_id_list_string)
    #
    #        # save the collection so we can associate images with it
    #        collection.save()
    #
    #        #apply permissions
    #        authorization.apply_collection_permissions(user, collection)
    #
    #        # now add all the images
    #        deployment_list = [int(x) for x in deployment_id_list_string.split(',')]
    #        for value in deployment_list:
    #            images = Image.objects.filter(pose__deployment=Deployment.objects.filter(id=value))
    #            collection.images.add(*images)
    #
    #        clid = collection.id
    #        msg="Your Project has been created successfully!"
    #
    #    except CollectionError as e:
    #        clid = None
    #        msg = e.msg
    #        #logger.error(msg)
    #
    #    except IntegrityError as e:
    #        clid = None
    #        msg = "This Project is to similar to an existing one. Please choose a more unique name."
    #
    #    except Exception as e:
    #        clid = None
    #        msg = "An unknown error has occurred during the creation of your Project..."
    #        print ("Exception Type: %s" % e.__class__)
    #        #logger.error(msg)
    #
    #    return clid, msg

    def create_collection(  self, user,
                            name, description,
                            deployment_list=None,
                            depth_range=None,
                            altitude_range=None,
                            bounding_boxes=None,
                            date_time_range=None):


        """Create a collection using all images in a deployment.

        :returns: the created collection.
        """
        try:

            # check user is logged in
            if user.is_anonymous() or not user.is_authenticated:
                raise CollectionError("You need to be logged in to create a Project...")


            # create and prefill the collection as much as possible
            collection = Collection()
            collection.name = name
            collection.description = description
            collection.owner = user
            collection.creation_date = datetime.now(tz=tzutc())
            collection.modified_date = datetime.now(tz=tzutc())
            collection.is_public = False
            collection.is_locked = True
            #collection.creation_info = "Deployments: {0}".format(deployment_id_list_string)

            # save the collection so we can associate images with it
            collection.save()
            #apply permissions
            authorization.apply_collection_permissions(user, collection)

            # get the measurement types we want to query
            measurement_types = ScientificMeasurementType.objects.all()
            #temperature = measurement_types.get(normalised_name="temperature")
            #salinity = measurement_types.get(normalised_name="salinity")
            altitude = measurement_types.get(normalised_name="altitude")

            # now add all the images
            dplinfo = ""
            depinfo = ""
            altinfo = ""
            datinfo = ""
            if deployment_list is not None:
                dplinfo = "{} deployments".format(len(deployment_list))
                for dplid in deployment_list:
                    value = int(dplid)
                    deployment = Deployment.objects.get(id=value)
                    images = Image.objects.filter(pose__deployment=deployment)

                    #dplinfo += deployment.short_name+" "
                    print dplinfo
                    #filter depth
                    if depth_range is not None:
                        print "depth filter", depth_range
                        images = images.filter(pose__depth__range=depth_range)
                        depinfo = " [depth:{} to {}m]".format(*depth_range)
                    #filter altitude
                    if altitude_range is not None:
                        print "altitude filter", altitude_range
                        images = images.filter(pose__scientificposemeasurement__measurement_type=altitude, pose__scientificposemeasurement__value__range=altitude_range)
                        #altinfo = "[altitude:" + altitude_range[0] + "-" + altitude_range[1] + "]"
                        altinfo = " [altitude:{} to {}m]".format(*altitude_range)
                    # filter dates
                    if date_time_range is not None:
                        print "depth filter", depth_range
                        images = images.filter(pose__date_time__range=date_time_range)
                        print "depth filter info"
                        datinfo = " [dates:{} to {}]".format(*date_time_range)
                    # Bounding boxes
                    if bounding_boxes is not None:
                        print "Bounding boxes ",bounding_boxes
                        for bbox in bounding_boxes:
                            bbox_tpl = tuple([float(x) for x in bbox.split(',')])
                            print bbox_tpl
                            bboximages = images.filter(pose__position__contained=Polygon.from_bbox(bbox_tpl))
                            collection.images.add(*bboximages)
                    else :
                        collection.images.add(*images)

                collection.creation_info = dplinfo+depinfo+altinfo+datinfo


            collection.save()
            print collection.creation_info

            clid = collection.id
            msg = "Your Project has been created successfully!"
            #return collection
        except CollectionError as e:
            clid = None
            msg = e.msg
            #logger.error(msg)

        except IntegrityError as e:
            clid = None
            msg = "This Project is to similar to an existing one. Please choose a more unique name."

        except Exception as e:
            clid = None
            msg = "An unknown error has occurred during the creation of your Project..."
            print ("Exception Type: %s" % e.__class__)
            print e.message
            #logger.error(msg)

        return clid, msg

    # NOTE: it may make sense to create one function for all the
    # different sampling methods instead of a separate one for each.
    def create_workset(self, user, name, description, ispublic, c_id, method, n=0, start_ind=False, stop_ind=False, img_list=None):
        """Create a workset (or child collection) from a parent collection

        returns: the created workset id (or None if error)
                 a status/error message
        """

        try:
            collection = Collection.objects.get(pk=c_id)

            # check user is logged in
            if user.is_anonymous() or not user.is_authenticated:
                raise CollectionError("You need to be logged in to create a Workset...")

            #check if the user has permission to do this
            if not user.has_perm('collection.view_collection', collection):
                raise CollectionError("Sorry. You don't have permission to create a Workset in this Project.")


            # Create new collection entry
            workset = Collection()
            workset.parent = collection
            workset.name = name
            workset.owner = user
            workset.creation_date = datetime.now(tz=tzutc())
            workset.modified_date = datetime.now(tz=tzutc())
            workset.is_public = ispublic
            workset.description = description
            workset.is_locked = True



            # subsample collection images and add to workset
            if method == "random":
                collection_images, start_ind, stop_ind = self.get_collection_images(collection, start_ind, stop_ind, n)
                wsimglist = sample(collection_images[start_ind:stop_ind:1], n)
                workset.creation_info = "{0} random images selected from {1} images starting at image {2}".format(n, stop_ind-start_ind, start_ind+1)

            elif method == "stratified":
                collection_images, start_ind, stop_ind = self.get_collection_images(collection, start_ind, stop_ind, n)
                wsimglist = collection_images[start_ind:stop_ind:n]
                workset.creation_info = "Every {0} image selected from {1} images starting at image {2}".format(self.num2ordstr(n), stop_ind-start_ind, start_ind+1)

            elif method == "upload" :
                wsimglist = []
                for imgname in img_list:
                    imgstr = os.path.splitext(imgname)[0]
                    print  imgstr
                    imgcount = Image.objects.filter(web_location__contains=imgstr).count()
                    #print imgcount
                    if imgcount < 1:
                        raise CollectionError("The image '{0}' does not exist. It may not be uploaded yet".format(imgname))
                    elif imgcount > 1:
                        raise CollectionError("There are multiple images matching the partial name '{0}'".format(imgname))
                    else :
                        img = Image.objects.get(web_location__contains=imgstr)
                        wsimglist.append(img)
                        #print img.id

                if len(wsimglist) <= 0:
                    raise CollectionError("No images could be found matching your list")
                workset.creation_info = "Uploaded list containing {0} pre-selected images".format(len(wsimglist))

            else:
                raise CollectionError("Unrecognised method argument for Workset creation")


            # save the workset so we can associate images with it
            workset.save()

            # Associate images with workset
            workset.images.add(*wsimglist)

            #apply permissions
            authorization.apply_collection_permissions(user, workset)

            wsid = workset.id
            msg="Your Workset has been created successfully!"

        except CollectionError as e:
            wsid = None
            msg = e.msg
            #logger.error(msg)

        except IntegrityError as e:
            wsid = None
            msg = "This Workset is to similar to an existing one. Please choose a more unique name."

        except Exception as e:
            wsid = None
            msg = "An unknown error has occurred during the creation of your Workset..."
            print ("Exception Type: %s" % e.__class__)
            #logger.error(msg)

        #print "Debug (wsid: {0}, msg: {1})".format(wsid, msg)
        return wsid, msg

    # get list of collection images
    def get_collection_images (self, collection, start_ind, stop_ind, n) :
        print "get_collection_images"
        collection_images = collection.images.all()
        start_ind = 0 if not start_ind else start_ind - 1
        stop_ind = collection_images.count() if (not stop_ind) or stop_ind > collection_images.count() else stop_ind - 1
        if stop_ind < start_ind:  # check the start and stop indices
            raise CollectionError("The Start index must be less than the Stop index.")
        if (stop_ind - start_ind) < n: # check that n < number of images
            raise CollectionError("Not enough images to subsample. The value for 'N' was greater than the total number of images.")
        return collection_images, start_ind, stop_ind

    # Format number as ordinal string
    def num2ordstr (self, n) :
        if 10 < n < 14:
            return "%sth" % n
        elif n % 10 == 1:
            return "%sst" % n
        elif n % 10 == 2:
            return "%snd" % n
        elif n % 10 == 3:
            return "%srd" % n
        else:
            return "%sth" % n

class CollectionError(Exception):
    """Exception raised for errors in the input.
    Attributes:
        msg  -- explanation of the error
    """
    def __init__(self, msg):
        self.msg = msg


class Collection(models.Model):
    """Collections are a set of images that a user works with.

    They contain 'worksets' and 'collections' in front end
    terminology. The only difference here is that collections
    don't have a parent whilst worksets do.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    is_locked = models.BooleanField()
    parent = models.ForeignKey('Collection', null=True, blank=True)
    images = models.ManyToManyField(Image, related_name='collections')
    creation_info = models.CharField(max_length=200)

    class Meta:
        unique_together = (('owner', 'name', 'parent'), )
        permissions = (
            ('view_collection', 'View the collection.'),
        )

    def __unicode__(self):
        description = u"Collection: {0}".format(self.name)

        if self.is_locked:
            description += u" - locked"
        return description
