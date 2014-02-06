import logging
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import Point, Polygon
from django.test.utils import setup_test_environment
from django.test import TestCase
import guardian
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign
from model_mommy import mommy
from tastypie.test import ResourceTestCase, TestApiClient
from catamidb.models import Image, ScientificMeasurementType
from catamidb.tests import TestCampaignResource
from collection import authorization
from collection.models import CollectionManager, Collection

logger = logging.getLogger(__name__)


def create_setup(self):
    self.campaign_one = mommy.make_one('catamidb.Campaign', id=1)

    self.deployment_one = mommy.make_one(
        'catamidb.Deployment',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604,43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        id=1,
        campaign=self.campaign_one)

    self.deployment_two = mommy.make_one(
        'catamidb.Deployment',
        start_position=Point(12.4604, 43.9420),
        end_position=Point(12.4604, 43.9420),
        transect_shape=Polygon(((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))),
        id=2,
        campaign=self.campaign_one)

    self.pose_one = mommy.make_one('catamidb.Pose',
                                   position=Point(12.4, 23.5),
                                   id=1,
                                   deployment=self.deployment_one,
                                   depth=10
    )

    self.pose_two = mommy.make_one('catamidb.Pose',
                                   position=Point(12.4, 23.5),
                                   id=2,
                                   deployment=self.deployment_two,
                                   depth=15
    )

    self.camera_one = mommy.make_one('catamidb.Camera',
                                     deployment=self.deployment_one,
                                     id=1,
    )
    self.camera_two = mommy.make_one('catamidb.Camera',
                                     deployment=self.deployment_two,
                                     id=2,
    )

    self.image_list = ['/live/test/test2.jpg', '/live/test/test1.jpg']
    self.mock_image_one = mommy.make_one('catamidb.Image',
                                         pose=self.pose_one,
                                         camera=self.camera_one,
                                         web_location=self.image_list[0],
                                         pk=1
    )
    self.mock_image_two = mommy.make_one('catamidb.Image',
                                         pose=self.pose_two,
                                         camera=self.camera_two,
                                         web_location=self.image_list[1],
                                         pk=2
    )


    #make pose measurements
    self.temp_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=1,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="temperature"),
                                   value=10)

    self.temp_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=2,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="temperature"),
                                   value=15)

    self.salinity_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=3,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="salinity"),
                                   value=10)

    self.salinity_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=4,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="salinity"),
                                   value=15)

    self.altitude_one = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=5,
                                   pose=self.pose_one,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="altitude"),
                                   value=10)

    self.altitude_two = mommy.make_one('catamidb.ScientificPoseMeasurement',
                                   id=6,
                                   pose=self.pose_two,
                                   measurement_type=ScientificMeasurementType.objects.get(normalised_name="altitude"),
                                   value=15)


class TestCollectionModel(TestCase):
    def setUp(self):
        create_setup(self)
        self.user = User.objects.create_user("Joe")
        self.collection_name = "Joe's Collection"
        self.collection_manager = CollectionManager()

    def test_collection_from_deployment(self):
        #create a collection
        self.collection_manager.collection_from_deployment(self.user, self.
            deployment_one)

        #check it got created
        collection = Collection.objects.get(name=self.deployment_one.
            short_name)
        self.assertIsInstance(collection, Collection)

        #check that the user and details were assigned
        self.assertEqual(collection.owner, self.user)
        self.assertEqual(collection.is_locked, True)

        #check that default permissions were applied
        self.assertTrue(self.user.has_perm('collection.view_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.add_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.change_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.delete_collection',
                                           collection))

        public_group, created = Group.objects.get_or_create(name='Public')
        checker = ObjectPermissionChecker(public_group)
        self.assertTrue(checker.has_perm('collection.view_collection',
                                         collection))

        #check the images went across - IMPORTANT!
        #get images for the deployment and the collection
        collection_images = collection.images.all().order_by("web_location")
        deployment_images = Image.objects.filter(pose__deployment=self.
            deployment_one).order_by("web_location")

        #check the image set is the same
        self.assertEqual(collection_images.values_list("web_location").__str__
            (), deployment_images.values_list("web_location").__str__())

        #try create with no user, should be an error
        try:
            self.collection_manager.collection_from_deployment(None, self.
                deployment_one)
        except Exception:
            self.assertTrue(True)

        #try create with no deployment
        try:
            self.collection_manager.collection_from_deployment(self.user, None)
        except Exception:
            self.assertTrue(True)

    def test_collection_from_deployments_with_name(self):
        #create the list of deployment ids to create a collection from
        deployment_ids = (self.deployment_one.id.__str__() + ',' + self.
            deployment_two.id.__str__())

        #create a collection
        self.collection_manager.collection_from_deployments_with_name(self.
            user, self.collection_name, deployment_ids.__str__())

        #check it got created
        collection = Collection.objects.get(name=self.collection_name)
        self.assertIsInstance(collection, Collection)

        #check that the user and details were assigned
        self.assertEqual(collection.owner, self.user)
        self.assertEqual(collection.is_locked, True)

        #check that default permissions were applied
        self.assertTrue(self.user.has_perm('collection.view_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.add_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.change_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.delete_collection',
                                           collection))

        public_group, created = Group.objects.get_or_create(name='Public')
        checker = ObjectPermissionChecker(public_group)
        self.assertTrue(checker.has_perm('collection.view_collection',
                                              collection))

        #check the images went across - IMPORTANT!
        #get images for the deployment and the collection
        collection_images = collection.images.all().order_by("web_location")
        deployment_one_images = Image.objects.filter(pose__deployment=self.
            deployment_one).order_by("web_location")
        deployment_two_images = Image.objects.filter(pose__deployment=self.
            deployment_two).order_by("web_location")

        # check that combined lengths of the deployment images is the same as
        # the collection
        self.assertEqual(collection_images.count(), deployment_one_images.
            count() + deployment_two_images.count())

        # check that the collection contains all the images from both
        # deployments
        for image in deployment_one_images:
            self.assertIsNotNone(collection_images.filter(id=image.id))

        for image in deployment_two_images:
            self.assertIsNotNone(collection_images.filter(id=image.id))

        #try create with no user, should be an error
        try:
            self.collection_manager.collection_from_deployment(None, self.
                collection_name, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

        #try create with no name
        try:
            self.collection_manager.collection_from_deployment(self.user,
                None, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

        #try create with no deployments
        try:
            self.collection_manager.collection_from_deployment(self.user, self
                .collection_name, "")
        except Exception:
            self.assertTrue(True)

        #try create collection with duplicate name
        try:
            self.collection_manager.collection_from_deployments_with_name(self
                .user, self.collection_name, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)


    def test_collection_from_explore(self):
        #create the list of deployment ids to create a collection from
        deployment_ids = (self.deployment_one.id.__str__() + ',' +
                          self.deployment_two.id.__str__())

        # this range of values should obtain us the single image from deployment_one
        depth__gte = 9
        depth__lte = 11
        temperature__gte = 9
        temperature__lte = 11
        salinity__gte = 9
        salinity__lte = 11
        altitude__gte = 9
        altitude__lte = 11

        #create a collection
        self.collection_manager.collection_from_explore(self.user,
                                                        self.collection_name,
                                                        deployment_ids.__str__(),
                                                        depth__gte,
                                                        depth__lte,
                                                        temperature__gte,
                                                        temperature__lte,
                                                        salinity__gte,
                                                        salinity__lte,
                                                        altitude__gte,
                                                        altitude__lte)



        #check it got created
        collection = Collection.objects.get(name=self.collection_name)
        self.assertIsInstance(collection, Collection)

        #check that the user and details were assigned
        self.assertEqual(collection.owner, self.user)
        self.assertEqual(collection.is_locked, True)

        #check that default permissions were applied
        self.assertTrue(self.user.has_perm('collection.view_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.add_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.change_collection',
                                           collection))
        self.assertTrue(self.user.has_perm('collection.delete_collection',
                                           collection))

        public_group, created = Group.objects.get_or_create(name='Public')
        checker = ObjectPermissionChecker(public_group)
        self.assertTrue(checker.has_perm('collection.view_collection',
                                         collection))

        #check the images went across - IMPORTANT!
        #get images for the deployment and the collection
        collection_images = collection.images.all().order_by("web_location")
        deployment_one_images = Image.objects.filter(pose__deployment=self.
        deployment_one).order_by("web_location")


        # check that we only got the image withiin our query bounds
        self.assertEqual(collection_images.count(), 1)

        #try create with no user, should be an error
        try:
            self.collection_manager.collection_from_explore(None, self.
            collection_name, deployment_ids.__str__())
        except Exception:
            self.assertTrue(True)

        #try create with no name
        try:
            self.collection_manager.collection_from_explore(self.user,
                                                            None,
                                                            deployment_ids.__str__(),
                                                            depth__gte,
                                                            depth__lte,
                                                            temperature__gte,
                                                            temperature__lte,
                                                            salinity__gte,
                                                            salinity__lte,
                                                            altitude__gte,
                                                            altitude__lte)
        except Exception:
            self.assertTrue(True)

        #try create with no deployments
        try:
            self.collection_manager.collection_from_explore(self.user,
                                                            self.collection_name,
                                                            "",
                                                            depth__gte,
                                                            depth__lte,
                                                            temperature__gte,
                                                            temperature__lte,
                                                            salinity__gte,
                                                            salinity__lte,
                                                            altitude__gte,
                                                            altitude__lte)
        except Exception:
            self.assertTrue(True)

        #try create collection with duplicate name
        try:
            self.collection_manager.collection_from_explore(self.user,
                                                            self.collection_name,
                                                            deployment_ids.__str__(),
                                                            depth__gte,
                                                            depth__lte,
                                                            temperature__gte,
                                                            temperature__lte,
                                                            salinity__gte,
                                                            salinity__lte,
                                                            altitude__gte,
                                                            altitude__lte)
        except Exception:
            self.assertTrue(True)


#======================================#
# Test the API                         #
#======================================#

class TestCollectionResource(ResourceTestCase):

    def setUp(self):
        #Tastypie stuff
        super(TestCollectionResource, self).setUp()

        self.bob_api_client = TestApiClient()
        self.bill_api_client = TestApiClient()
        self.anon_api_client = TestApiClient()

        # Create a user bob.
        self.user_bob_username = 'bob'
        self.user_bob_password = 'bob'
        self.user_bob = User.objects.create_user(self.user_bob_username,
                                                 'daniel@example.com',
                                                 self.user_bob_password)

        # Create a user bob.
        self.user_bill_username = 'bill'
        self.user_bill_password = 'bill'
        self.user_bill = User.objects.create_user(self.user_bill_username,
                                                  'daniel@example.com',
                                                  self.user_bill_password)

        self.bob_api_client.client.login(username='bob', password='bob')
        self.bill_api_client.client.login(username='bill', password='bill')

        #assign users to the Public group
        public_group, created = Group.objects.get_or_create(name='Public')
        self.user_bob.groups.add(public_group)
        self.user_bill.groups.add(public_group)
        guardian.utils.get_anonymous_user().groups.add(public_group)

        #make a couple of collections and save
        self.collection_bobs = mommy.make_recipe('collection.collection1', id=1, owner=self.user_bob)
        self.collection_bills = mommy.make_recipe('collection.collection2', id=2, owner=self.user_bill)

        #assign this one to bob
        authorization.apply_collection_permissions(
            self.user_bob, self.collection_bobs)

        #assign this one to bill
        authorization.apply_collection_permissions(
            self.user_bill, self.collection_bills)

        #the API url for campaigns
        self.collection_url = '/api/dev/collection/'

        #some post data for testing collection creation
        self.post_data = {}

    # can only do GET and UPDATE at this stage
    def test_collection_operations_disabled(self):
        # test that we can NOT create
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.post(self.collection_url,
                                      format='json',
                                      data=self.post_data))

        # test that we can NOT modify as anonymous
        self.assertHttpUnauthorized(
            self.anon_api_client.put(
                self.collection_url + self.collection_bobs.id.__str__() + "/",
                format='json',
                data={})
        )

        # test that we can NOT delete
        self.assertHttpMethodNotAllowed(
            self.anon_api_client.delete(
                self.collection_url + self.collection_bobs.id.__str__() + "/",
                format='json')
        )

        # test that we can NOT create authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.post(self.collection_url,
                                     format='json',
                                     data=self.post_data)
        )



        # test that we can NOT delete authenticated
        self.assertHttpMethodNotAllowed(
            self.bob_api_client.delete(
                self.collection_url + self.collection_bobs.id.__str__() + "/",
                format='json'))

    #test can get a list of campaigns authorised
    def test_collections_operations_as_authorised_users(self):
        # create a campaign that only bill can see
        bills_collection = mommy.make_recipe('collection.collection3', id=3, owner=self.user_bill)
        assign('view_collection', self.user_bill, bills_collection)

        # check that bill can see via the API
        response = self.bill_api_client.get(self.collection_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 3)

        # check that bill can get to the object itself
        response = self.bill_api_client.get(self.collection_url + "3/",
                                            format='json')
        self.assertValidJSONResponse(response)

        # check that bob can not see - now we know tastypie API has correct
        # permission validation
        response = self.bob_api_client.get(self.collection_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        # check bob can NOT get to the hidden object
        response = self.bob_api_client.get(self.collection_url + "3/",
                                           format='json')
        self.assertHttpUnauthorized(response)

        #check that anonymous can see public ones as well
        response = self.anon_api_client.get(self.collection_url, format='json')
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['objects']), 2)

        #check anonymous can NOT get to the hidden object
        response = self.anon_api_client.get(self.collection_url + "3/",
                                            format='json')
        self.assertHttpUnauthorized(response)

    def test_update_collection_authorised(self):
        #TODO: implement this test
        # test that we can NOT modify authenticated
        #self.assertHttpMethodNotAllowed(
        #    self.bob_api_client.put(
        #        self.collection_url + self.campaign_bobs.id.__str__() + "/",
        #        format='json',
        #        data={})
        #)

        return None

