# Create your views here.
from django.template import RequestContext

from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import guardian
from guardian.shortcuts import get_objects_for_user
from waffle.decorators import waffle_switch
from django.core.urlresolvers import reverse
import logging

#for the geoserver proxy
from django.views.decorators.csrf import csrf_exempt
import httplib2

#not API compliant - to be removed after the views are compliant
from catamidb.api import ImageResource
from catamidb.models import Pose, Image, Campaign, AUVDeployment, \
    BRUVDeployment, DOVDeployment, Deployment, TIDeployment, TVDeployment
from django.contrib.gis.geos import fromstr
from django.db.models import Max, Min
import simplejson
from django.conf import settings
from collection.api import CollectionResource
from collection.models import Collection, CollectionManager

from webinterface.forms import CreateCollectionForm, CreateWorksetForm, CreateWorksetAndAnnotation, CreateCollectionExploreForm, CreatePointAnnotationSet, CreateWorksetFromImagelist
from userena.forms import AuthenticationForm, SignupForm

import HTMLParser

# DajaxIce
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

logger = logging.getLogger(__name__)

def check_permission(user, permission, object):
    """
    A helper function for checking permissions on object. Need this
    because of the anonymous user.
    """

    #just make sure we get the anonymous user from the database - so we can user permissions
    if user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    return user.has_perm(permission, object)

def get_objects_for_user_wrapper(user, permission_array):
    """
    Helper function that wraps get_objects_for_user, I put this here to
    save having to obtain the anonymous user all the time.
    """
    #just make sure we get the anonymous user from the database - so we can user permissions
    if user.is_anonymous():
        user = guardian.utils.get_anonymous_user()

    return get_objects_for_user(user, permission_array)


#front page and zones
def index(request):
    """@brief returns root catami html
    """
    #return HttpResponseRedirect('viewproject')
    return render_to_response('webinterface/index.html',RequestContext(request))

# Info pages
def faq(request):
    return render_to_response('webinterface/faq.html', {},
                              RequestContext(request))


def contact(request):
    return render_to_response('webinterface/contact.html', {},
                              RequestContext(request))


def about(request):
    return render_to_response('webinterface/about.html', {},
                              RequestContext(request))


def howto(request):
    return render_to_response('webinterface/howto.html', {},

                              RequestContext(request))


# Explore pages
def explore(request):
    """@brief Campaign list html for entire database

    """
    return render_to_response('webinterface/explore.html',
                              {'WMS_URL': settings.WMS_URL,
                               'WMS_layer_name': settings.WMS_LAYER_NAME},
                              context_instance=RequestContext(request))


# Explore pages
def explore_campaign(request, campaign_id):
    return render_to_response('webinterface/explore.html', {},
                              context_instance=RequestContext(request))

# Collection pages
@waffle_switch('Collections')
def projects(request):
#    my_collections_error = ''
#    public_collections_error =''
#
#    collection_list = CollectionResource()
#    try:
#        cl_my_rec = collection_list.obj_get_list(request, owner=request.user.id, parent=None)
#        if (len(cl_my_rec) == 0):
#            my_collections_error = 'Sorry, you don\'t seem to have any collections in your account.'
#
#    except:
#        cl_my_rec = ''
#        if (request.user.is_anonymous):
#            my_collections_error = 'Sorry, you dont appear to be logged in. Please login and try again.'
#        else:
#            my_collections_error = 'An undetermined error has occured. Please contact support'
#
#    try:
#        cl_pub_rec = collection_list.obj_get_list(request, is_public=True, parent=None)
#        if (len(cl_pub_rec) == 0):
#            public_collections_error = 'Sorry, there don\'t seem to be any public collections right now.'
#
#    except:
#        cl_pub_rec = ''
#        if (request.user.is_anonymous):
#            public_collections_error = 'Sorry, public collections arent working for anonymous users right now. Please login and try again.'
#        else:
#            public_collections_error = 'An undetermined error has occured. Please contact support'

    return render_to_response('webinterface/projects.html',
                              #        {"my_rec_cols": cl_my_rec,
                              #         "my_collections_error": my_collections_error,
                              #         "pub_rec_cols": cl_pub_rec,
                              #         "public_collections_error":public_collections_error,
                              {'WMS_URL': settings.WMS_URL,
                               #imported from settings
                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME},
                              RequestContext(request))

# @waffle_switch('Collections')
# def my_collections(request):
#     error_description = ''
#
#     collection_list = CollectionResource()
#
#     try:
#         cl = collection_list.obj_get_list(request, owner=request.user.id)
#         if (len(cl) == 0):
#             error_description = 'Sorry, you don\'t seem to have any collections in your account.'
#     except:
#         cl = ''
#         if (request.user.is_anonymous):
#             error_description = 'Sorry, you dont appear to be logged in. Please login and try again.'
#         else:
#             error_description = 'An undetermined error has occured. Please contact support'
#
#     return render_to_response('webinterface/mycollections.html',
#         {"collections": cl,
#         "listname":"cl_pub_all",
#         "error_description":error_description},
#         RequestContext(request))
#
# @waffle_switch('Collections')
# def public_collections(request):
#     error_description = ''
#
#     collection_list = CollectionResource()
#     try:
#         cl = collection_list.obj_get_list(request, is_public=True)
#         if (len(cl) == 0):
#             error_description = 'Sorry, there don\'t seem to be any public collections right now.'
#     except:
#         cl = ''
#         if (request.user.is_anonymous):
#             error_description = 'Sorry, public collections arent working for anonymous users right now. Please login and try again.'
#         else:
#             error_description = 'An undetermined error has occured. Please contact support'
#
#     return render_to_response('webinterface/publiccollections.html',
#         {"collections": cl,
#          "listname":"cl_pub_all",
#         "error_description":error_description},
#          RequestContext(request))

## view collection table views
def public_collections_all(request):
    collection_list = CollectionResource()
    cl = collection_list.obj_get_list()
    return render_to_response('webinterface/publiccollections.html', {"collections": cl, "listname":"cl_pub_all"}, RequestContext(request))



@waffle_switch('Collections')
def view_collection(request, collection_id):
    wsform_rand = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'random','n':100})
    wsform_strat = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'stratified','n':100})
    asform = CreatePointAnnotationSet()

    # check for optional get parameters
    # This avoids needing to specify a new url and view for each optional parameter
    workset_id = request.GET.get("wsid", "")
    annotation_id = request.GET.get("asid", "")

    #check change permissions
    collection = Collection.objects.get(pk=collection_id)

    change_collection = check_permission(request.user, 'collection.view_collection', collection)

    return render_to_response('webinterface/viewcollection.html',
#    return render_to_response('webinterface/viewcollectionalternative.html',
                              {'wsform_rand' : wsform_rand,
                               'wsform_strat' : wsform_strat,
                               'asform' : asform,
                               'collection_id': collection_id,
                               'workset_id': workset_id,
                               "annotation_id": annotation_id,
                               'WMS_URL': settings.WMS_URL,
                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME,
                               'change_collection': change_collection},
                              RequestContext(request))

@waffle_switch('Collections')
def view_project(request):

    # check for optional get parameters
    # This avoids needing to specify a new url and view for each optional parameter
    collection_id = request.GET.get("clid", "")
    workset_id = request.GET.get("wsid", "")
    annotation_id = request.GET.get("asid", "")

    # Forms
    wsasform = CreateWorksetAndAnnotation(initial={'c_id': collection_id, 'n':100})


    #check change permissions
    collection = Collection.objects.get(pk=collection_id)
    change_collection = check_permission(request.user, 'collection.change_collection', collection)

    return render_to_response('webinterface/project.html',
        #    return render_to_response('webinterface/viewcollectionalternative.html',
        {'wsasform' : wsasform,
         'collection_id': collection_id,
         'workset_id': workset_id,
         "annotation_id": annotation_id,
         'WMS_URL': settings.WMS_URL,
         'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME,
         'change_collection': change_collection},
        RequestContext(request))


# NEW VIEWS #########################################################
def project(request):

    # check for optional get parameters
    # This avoids needing to specify a new url and view for each optional parameter
    clid = request.GET.get("clid", "0") if request.GET.get("clid", "") else 0
    wsid = request.GET.get("wsid", "0") if request.GET.get("wsid", "") else 0
    asid = request.GET.get("asid", "0") if request.GET.get("asid", "") else 0
    imid = request.GET.get("imid", "0") if request.GET.get("imid", "") else 0

    # Forms
    clform = CreateCollectionForm()
    wsform = CreateWorksetForm(initial={'c_id': clid, 'method': 'random', 'n': 100, 'start_ind': 0, 'stop_ind': 0})
    ulwsform = CreateWorksetFromImagelist(initial={'c_id': clid})
    asform = CreatePointAnnotationSet(initial={'count': 50})
    aform = AuthenticationForm()
    suform = SignupForm()


    return render_to_response('webinterface/viewproject.html',
        #    return render_to_response('webinterface/viewcollectionalternative.html',
        {'clid': clid,
         'wsid': wsid,
         "asid": asid,
         "imid": imid,
         "clform" : clform,
         "wsform" : wsform,
         "ulwsform" : ulwsform,
         "asform" : asform,
         "aform" : aform,
         "suform" : suform,
         "GEOSERVER_URL": settings.GEOSERVER_URL},
        RequestContext(request))

#####################################################################
# NEW MAPS ##########################################################
def map(request):

    # check for optional get parameters
    # This avoids needing to specify a new url and view for each optional parameter
    clid = request.GET.get("clid", "0") if request.GET.get("clid", "") else 0
    wsid = request.GET.get("wsid", "0") if request.GET.get("wsid", "") else 0
    asid = request.GET.get("asid", "0") if request.GET.get("asid", "") else 0
    imid = request.GET.get("imid", "0") if request.GET.get("imid", "") else 0

    return render_to_response('webinterface/viewmap.html',
        {'clid': clid,
         'wsid': wsid,
         "asid": asid,
         "imid": imid,
         'WMS_URL': settings.WMS_URL,
         'WMS_layer_name': settings.WMS_LAYER_NAME},
        RequestContext(request))

#####################################################################




#@waffle_switch('Collections')
#def view_workset(request, collection_id, workset_id):
#    wsform_rand = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'random'})
#    wsform_strat = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'stratified'})
#    asform = CreatePointAnnotationSet()
#
#
#    #check change permissions
#    collection = Collection.objects.get(pk=collection_id)
#
#    change_collection = check_permission(request.user, 'collection.change_collection', collection)
#
#    return render_to_response('webinterface/viewcollection.html',
##    return render_to_response('webinterface/viewworkset.html',
#                              {'wsform_rand' : wsform_rand,
#                               'wsform_strat' : wsform_strat,
#                               'asform' : asform,
#                               'collection_id': collection_id,
#                               'workset_id': workset_id,
#                               'WMS_URL': settings.WMS_URL,
#                               'WMS_layer_name': settings.WMS_COLLECTION_LAYER_NAME,
#                               'change_collection': change_collection},
#                              RequestContext(request))


# view collection table views
# def public_collections_all(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list()
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_all"}, RequestContext(request))
#
# def public_collections_recent(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list()
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"pub_rec"}, RequestContext(request))
#
# def my_collections_all(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list(request,owner=request.user.id)
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_all"}, RequestContext(request))
#
# def my_collections_recent(request):
#     collection_list = CollectionResource()
#     cl = collection_list.obj_get_list(request,owner=request.user.id)
#     return render_to_response('webinterface/dataviews/collectiontable.html', {"collections": cl, "listname":"my_rec"}, RequestContext(request))

# collection object tasks
@waffle_switch('Collections')
def delete_collection(request):
    return None


@waffle_switch('Collections')
def flip_public_collection(request):
    return None


# Subset pages
@waffle_switch('Collections')
def view_subset(request):
    return render_to_response('webinterface/viewsubset.html', {},
                              RequestContext(request))


@waffle_switch('Collections')
def all_subsets(request, collection_id):
    return render_to_response('webinterface/allsubsets.html',
                              {"collection_id": collection_id},
                              RequestContext(request))


@waffle_switch('Collections')
def my_subsets(request):
    return render_to_response('webinterface/mysubsets.html', {},
                              RequestContext(request))


@waffle_switch('Collections')
def public_subsets(request):
    return render_to_response('webinterface/publicsubsets.html', {},
                              RequestContext(request))


# Single image pages
def image_view(request):
    return render_to_response('webinterface/imageview.html', {},
                              RequestContext(request))


def image_annotate(request,image_id):
    apistring = request.GET.get("apistring", "")
    offset = request.GET.get("offset", "")
    annotation_id = request.GET.get("asid", "")

    return render_to_response('webinterface/imageview.html', #imageannotate.html',
        {"image_id": image_id, "offset": offset, "apistring": apistring, "annotation_id": annotation_id},
        RequestContext(request))


def image_edit(request):
    return render_to_response('webinterface/imageedit.html', {},
                              RequestContext(request))


#Force views from old view setup (NOT API COMPLIANT)
def data(request):
    return render_to_response('webinterface/Force_views/index.html', {},
                              RequestContext(request))


def deployments(request):
    """@brief Deployment list html for entire database

    """
    auv_deployment_list = AUVDeployment.objects.all()
    bruv_deployment_list = BRUVDeployment.objects.all()
    dov_deployment_list = DOVDeployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentIndex.html',
        {'auv_deployment_list': auv_deployment_list,
         'bruv_deployment_list': bruv_deployment_list,
         'dov_deployment_list': dov_deployment_list},
        context_instance=RequestContext(request))


def deployments_map(request):
    """@brief Deployment map html for entire database

    """
    latest_deployment_list = Deployment.objects.all()
    return render_to_response(
        'webinterface/Force_views/DeploymentMap.html',
        {'latest_deployment_list': latest_deployment_list},
        context_instance=RequestContext(request))


def auvdeployments(request):
    """@brief AUV Deployment list html for entire database

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])

    latest_auvdeployment_list = AUVDeployment.objects.filter(campaign__in=latest_campaign_list)

    return render_to_response(
        'webinterface/Force_views/auvDeploymentIndex.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))


def auvdeployments_map(request):
    """@brief AUV Deployment map html for entire database

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])

    latest_auvdeployment_list = AUVDeployment.objects.filter(
        campaign__in=latest_campaign_list
    )

    return render_to_response(
        'webinterface/Force_views/auvDeploymentMap.html',
        {'latest_auvdeployment_list': latest_auvdeployment_list},
        context_instance=RequestContext(request))

def auvdeployment_detail(request, auvdeployment_id):
    """@brief AUV Deployment map and data plot for specifed AUV deployment

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign'])

    auvdeployment_object = {}

    try:
        auvdeployment_object = list(AUVDeployment.objects.filter(
            id=auvdeployment_id, campaign__in=latest_campaign_list))[0]

    #if it doesn't exist or we dont have permission then go back to the main list
    except Exception:
        return auvdeployments(request)

    return render_to_response(
        'webinterface/Force_views/auvdeploymentDetail.html',
        {'auvdeployment_object': auvdeployment_object,
         'WMS_URL': settings.WMS_URL,
         'WMS_layer_name': settings.WMS_LAYER_NAME,
         'deployment_id': auvdeployment_object.id},
        context_instance=RequestContext(request))

def campaigns(request):
    """@brief Campaign list html for entire database

    """

    latest_campaign_list = get_objects_for_user_wrapper(request.user, [
        'catamidb.view_campaign']) #Campaign.objects.all()
    campaign_rects = list()

    for campaign in latest_campaign_list:
        auv_deployment_list = AUVDeployment.objects.filter(campaign=campaign)
        bruv_deployment_list = BRUVDeployment.objects.filter(campaign=campaign)
        dov_deployment_list = DOVDeployment.objects.filter(campaign=campaign)
        if len(auv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)
        if len(bruv_deployment_list) > 0:
            sm = fromstr(
                'MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(
                    campaign=campaign).extent())
            campaign_rects.append(sm.envelope.geojson)

    return render_to_response(
        'webinterface/Force_views/campaignIndex.html',
        {'latest_campaign_list': latest_campaign_list,
         'campaign_rects': campaign_rects},
        context_instance=RequestContext(request))


def campaign_detail(request, campaign_id):
    """@brief Campaign html for a specifed campaign object

    """

    try:
        campaign_object = Campaign.objects.get(id=campaign_id)

        #check for permissions
        if not check_permission(request.user, 'catamidb.view_campaign', campaign_object):
            raise Campaign.DoesNotExist

    except Campaign.DoesNotExist:
        error_string = 'This is the error_string'
        return render_to_response(
            'webinterface/Force_views/data_missing.html',
            context_instance=RequestContext(request))
    campaign_rects = list()
    #djf = Django.Django(geodjango="extent", properties=[''])

    auv_deployment_list = AUVDeployment.objects.filter(
        campaign=campaign_object)
    bruv_deployment_list = BRUVDeployment.objects.filter(
        campaign=campaign_object)
    dov_deployment_list = DOVDeployment.objects.filter(
        campaign=campaign_object)
    ti_deployment_list = TIDeployment.objects.filter(campaign=campaign_object)
    tv_deployment_list = TVDeployment.objects.filter(campaign=campaign_object)
    #geoj = GeoJSON.GeoJSON()
    #sm = AUVDeployment.objects.filter(transect_shape__bbcontains=pnt_wkt)
    #sm = AUVDeployment.objects.all().extent
    #sm = fromstr('MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(campaign=campaign_object).extent())

    sm = ' '
    if len(auv_deployment_list) > 0:
        sm = fromstr(
            'MULTIPOINT (%s %s, %s %s)' % AUVDeployment.objects.filter(
                campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    if len(bruv_deployment_list) > 0:
        sm = fromstr(
            'MULTIPOINT (%s %s, %s %s)' % BRUVDeployment.objects.filter(
                campaign=campaign_object).extent())
        campaign_rects.append(sm.envelope.geojson)
    try:
        sm_envelope = sm.envelope.geojson
    except AttributeError:
        sm_envelope = ''

    return render_to_response(
        'webinterface/Force_views/campaign_detail.html',
        {'campaign_object': campaign_object,
         'auv_deployment_list': auv_deployment_list,
         'bruv_deployment_list': bruv_deployment_list,
         'dov_deployment_list': dov_deployment_list,
         'ti_deployment_list': ti_deployment_list,
         'tv_deployment_list': tv_deployment_list,

         'campaign_as_geojson': sm_envelope},
        context_instance=RequestContext(request))


@csrf_exempt
def get_multiple_deployment_extent(request):
    if request.method == 'POST':  # If the form has been submitted...
        deployment_ids = request.POST.get('deployment_ids')
        deployment_ids = deployment_ids.__str__().split(",")
        extent = Pose.objects.filter(
            deployment_id__in=deployment_ids).extent().__str__()

        response_data = {"extent": extent}
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype="application/json")

    return HttpResponse(
        simplejson.dumps({"message": "GET operation invalid, must use POST."}),
        mimetype="application/json")


@csrf_exempt
def get_collection_extent(request):
    if request.method == 'POST':  # If the form has been submitted...
        collection_id = request.POST.get('collection_id')
        image_set = Collection.objects.get(id=collection_id).images.all()
        pose_id_set = image_set.values_list("pose_id")

        extent = Pose.objects.filter(id__in=pose_id_set).extent().__str__()

        response_data = {"extent": extent}
        return HttpResponse(simplejson.dumps(response_data),
                            mimetype="application/json")

    return HttpResponse(
        simplejson.dumps({"message": "GET operation invalid, must use POST."}),
        mimetype="application/json")


@csrf_exempt
def create_collection_from_deployments(request):

    if request.method == 'POST':  # If the form has been submitted...
        form = CreateCollectionForm(
            request.POST)  # A form bound to the POST data

        if form.is_valid():  # All validation rules pass
            # make a new collection here from the deployment list
            CollectionManager().collection_from_deployments_with_name(
                request.user, request.POST.get('collection_name'),
                request.POST.get('deployment_ids'))
            return HttpResponseRedirect('/projects')  # Redirect after POST

    return render(request, 'noworky.html', {'form': form, })

@csrf_exempt
def create_collection_from_explore(request):

    if request.method == 'POST':  # If the form has been submitted...
        form = CreateCollectionExploreForm(
            request.POST)  # A form bound to the POST data
        print "post"
        print request._body
        if form.is_valid():  # All validation rules pass
            print "valid"
            # make a new collection here from the deployment list
            CollectionManager().collection_from_explore(
                request.user, request.POST.get('collection_name'),
                request.POST.get('deployment_ids'),
                request.POST.get('depth__gte'),
                request.POST.get('depth__lte'),
                request.POST.get('temperature__gte'),
                request.POST.get('temperature__lte'),
                request.POST.get('salinity__gte'),
                request.POST.get('salinity__lte'),
                request.POST.get('altitude__gte'),
                request.POST.get('altitude__lte')
                )
            return HttpResponseRedirect('/projects')  # Redirect after POST

    return render(request, 'noworky.html', {'form': form, })


@csrf_exempt
def proxy(request):

    url = request.GET.get('url',None)

    conn = httplib2.Http()
    if request.method == "GET":
        resp, content = conn.request(url, request.method)
        return HttpResponse(content)
    elif request.method == "POST":
        url = url
        data = request.body
        resp, content = conn.request(url, request.method, data)
        return HttpResponse(content)

def dynamic_style(request):
    """Return XML Style to colour geoserver maps.
    
    Takes GET parameters min, max and prop to designate what
    to colour by.
    """
    context = {}
    rcon = RequestContext(request)

    minimum = request.GET.get("min", 20.0)
    maximum = request.GET.get("max", 50.0)
    property_name = request.GET.get("prop", "depth")

    colour_map = [(minimum, "#FF0000"), (maximum, "#0000FF")]

    context['colourmap'] = colour_map
    context['property_name'] = property_name

    return render_to_response('geoserver/sldtemplate.xml', context, rcon, mimetype="application/xml")

def dynamic_Simplestyle(request):
    """Return XML Style to colour geoserver maps.
    
    Takes GET parameters colour and size to designate what
    to colour by.
    """
    context = {}
    rcon = RequestContext(request)

    name = request.GET.get("name", "catami:collection_images")
    colour = request.GET.get("colour", "#FF0000");
    size = request.GET.get("size", 6);

    context['name'] = name
    context['colour'] = colour
    context['size'] = size

    return render_to_response('geoserver/sldSimpletemplate.xml', context, rcon, mimetype="application/xml")

def dynamic_Deploymentstyle(request):
    """Return XML Style to colour geoserver maps.
    
    Takes GET parameters colour and size to designate what
    to colour by.
    """
    context = {}
    rcon = RequestContext(request)

    return render_to_response('geoserver/sldDeploymentTemplate.xml', context, rcon, mimetype="application/xml")

def dynamic_DeploymentSimplestyle(request):
    """Return XML Style to colour geoserver maps.
    
    Takes GET parameters colour and size to designate what
    to colour by.
    """
    context = {}
    rcon = RequestContext(request)

    colour = request.GET.get("colour", "#FF0000");
    size = request.GET.get("size", 6);

    context['colour'] = colour
    context['size'] = size

    return render_to_response('geoserver/sldDeploymentSimpleTemplate.xml', context, rcon, mimetype="application/xml")

def dynamic_colourmap(request):
    """Return SVG Image to denote colour map for geoserver.

    Takes GET parameters min, max and prop to designate what 
    to colour by.
    """
    import math
    context = {}
    rcon = RequestContext(request)

    # get the entries we are using
    minimum = request.GET.get("min", 20.0)
    maximum = request.GET.get("max", 50.0)
    property_name = request.GET.get("prop", "depth")
    height = request.GET.get("height", 300)

    # allow 30px per mark
    max_labels = math.floor(height / 30)

    # pre calculations to work out the scale with nicer numbers
    # and intervals
    scale_range = maximum - minimum
    approx_interval = scale_range / max_labels
    logged = math.log10(approx_interval)
    order = math.floor(logged)

    # find the nicest interval to represent
    if logged < order + 0.33333333:
        interval = 2 * 10 ** order
    elif logged < order + 0.6666666:
        interval = 5 * 10 ** order
    else:
        interval = 10 * 10 ** order

    # get rid of the decimal point if we don't need it
    if interval > 0.99:
        interval = int(interval)

    # find the new nicer limits
    mult_minimum = int(minimum // interval)
    mult_maximum = int(maximum // interval + 1)

    # check if the maximum was already a nice number
    if math.fabs((mult_maximum - 1) * interval - maximum) < interval * 0.01:
        mult_maximum = mult_maximum - 1

    labels = list(i * interval for i in xrange(mult_minimum, mult_maximum + 1))
    colour_map = [(minimum, "#FF0000"), (maximum, "#0000FF")]

    positions = [height * i / (len(labels) - 1) for i in xrange(len(labels))]

    context['colourmap'] = colour_map
    context['property_name'] = property_name
    context['map_intervals'] = len(colour_map) - 1
    context['height'] = height
    context['labels'] = zip(labels, positions)

    return render_to_response('geoserver/colourmap.svg', context, rcon, mimetype="application/xml")
