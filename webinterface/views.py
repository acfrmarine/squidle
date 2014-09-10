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
    BRUVDeployment, DOVDeployment, Deployment, TIDeployment, TVDeployment, ScientificPoseMeasurement
from django.contrib.gis.geos import fromstr
from django.db.models import Max, Min
import simplejson
from django.conf import settings
from collection.api import CollectionResource
from collection.models import Collection, CollectionManager
from annotations.models import PointAnnotation, PointAnnotationSet, AnnotationCode

from webinterface.forms import dataset_forms, CreateCollectionForm, CreateWorksetForm, CreateWorksetAndAnnotation, CreateCollectionExploreForm, CreatePointAnnotationSet, CreateWorksetFromImagelist
from userena.forms import AuthenticationForm, SignupForm

from django.db.models import Max

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
    return render_to_response('webinterface/index.html', RequestContext(request))

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
    return render_to_response('webinterface/publiccollections.html', {"collections": cl, "listname": "cl_pub_all"},
                              RequestContext(request))


@waffle_switch('Collections')
def view_collection(request, collection_id):
    wsform_rand = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'random', 'n': 100})
    wsform_strat = CreateWorksetForm(initial={'c_id': collection_id, 'method': 'stratified', 'n': 100})
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
                              {'wsform_rand': wsform_rand,
                               'wsform_strat': wsform_strat,
                               'asform': asform,
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
    wsasform = CreateWorksetAndAnnotation(initial={'c_id': collection_id, 'n': 100})


    #check change permissions
    collection = Collection.objects.get(pk=collection_id)
    change_collection = check_permission(request.user, 'collection.change_collection', collection)

    return render_to_response('webinterface/project.html',
                              #    return render_to_response('webinterface/viewcollectionalternative.html',
                              {'wsasform': wsasform,
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
    # clform = CreateCollectionForm()
    # wsform = CreateWorksetForm(initial={'c_id': clid, 'method': 'random', 'n': 100, 'start_ind': 0, 'stop_ind': 0})
    # ulwsform = CreateWorksetFromImagelist(initial={'c_id': clid})
    # asform = CreatePointAnnotationSet(initial={'count': 50})
    aform = AuthenticationForm()
    suform = SignupForm()

    return render_to_response('webinterface/viewproject.html',
                              #    return render_to_response('webinterface/viewcollectionalternative.html',
                              {'clid': clid,
                               'wsid': wsid,
                               "asid": asid,
                               "imid": imid,
                               "clform": dataset_forms["clform"](),
                               "wsform": dataset_forms["wsform"](initial={'c_id': clid, 'method': 'random', 'n': 100, 'start_ind': 0, 'stop_ind': 0}),
                               "ulwsform": dataset_forms["ulwsform"](initial={'c_id': clid}),
                               "asform": dataset_forms["asform"](initial={'count': 50}),
                               "aform": aform,
                               "suform": suform,
                               "GEOSERVER_URL": settings.GEOSERVER_URL},
                              RequestContext(request))

######################################################################
## NEW MAPS ##########################################################
#def map(request):
#
#    # check for optional get parameters
#    # This avoids needing to specify a new url and view for each optional parameter
#    clid = request.GET.get("clid", "0") if request.GET.get("clid", "") else 0
#    wsid = request.GET.get("wsid", "0") if request.GET.get("wsid", "") else 0
#    asid = request.GET.get("asid", "0") if request.GET.get("asid", "") else 0
#    imid = request.GET.get("imid", "0") if request.GET.get("imid", "") else 0
#
#    return render_to_response('webinterface/viewmap.html',
#        {'clid': clid,
#         'wsid': wsid,
#         "asid": asid,
#         "imid": imid,
#         'WMS_URL': settings.WMS_URL,
#         'WMS_layer_name': settings.WMS_LAYER_NAME},
#        RequestContext(request))

#####################################################################


def download_csv(request):
    #from djqscsv import render_to_csv_response
    import pandas as pd
    import datetime
    import cStringIO

    clid = request.GET.get("clid", "0") if request.GET.get("clid", "") else 0
    asid = request.GET.get("asid", "0") if request.GET.get("asid", "") else 0
    format = request.GET.get("format", "")

    if asid:
        annotation = PointAnnotationSet.objects.get(pk=asid)
        filename = 'annotation-%s-%s-%s.csv' % (annotation.name, format, str(datetime.date.today()))


        if format=="rawdbdump" :
            point_annotations = PointAnnotation.objects.filter(annotation_set=annotation).values('image_id',
                                                                                                 'image__web_location',
                                                                                                 'x',
                                                                                                 'y',
                                                                                                 'id',
                                                                                                 'label_id',
                                                                                                 'label__caab_code',
                                                                                                 'label__code_name',
                                                                                                 'label__cpc_code',
                                                                                                 'qualifiers__modifier_name'
            )

            # Create pandas data frame, fill holes with blank strings
            pts_df = pd.DataFrame(list(point_annotations)).fillna('')

            # Rename fields
            point_renames = {
                'image__web_location': 'web_location',
                'label__caab_code': 'caab',
                'label__code_name': 'name',
                'label__cpc_code': 'code',
                'qualifiers__modifier_name': 'modifiers'
            }
            pts_df.rename(columns=point_renames, inplace=True)

            # Group by image and point and aggregate modifiers, then reset indexes
            pts_df = pts_df.groupby(['image_id', 'id']).aggregate({'modifiers': lambda x: ', '.join(x),
                                                                   'name': lambda x: x.iat[0],
                                                                   'caab': lambda x: x.iat[0],
                                                                   'code': lambda x: x.iat[0],
                                                                   'label_id': lambda x: x.iat[0],
                                                                   'x': lambda x: x.iat[0],
                                                                   'y': lambda x: x.iat[0],
                                                                   'web_location': lambda x: x.iat[0],
            }).delevel(['image_id', 'id'])
            pts_df.pop('id')  # remove point ID from output
            out_df = pts_df
            #return render_to_csv_response(point_annotations, filename=filename)

        else:
            point_annotations = PointAnnotation.objects.filter(annotation_set=annotation).values('image_id',
                                                                                                 #'x',
                                                                                                 #'y',
                                                                                                 'id',
                                                                                                 'label_id',
                                                                                                 'label__caab_code',
                                                                                                 'label__code_name',
                                                                                                 'label__cpc_code',
                                                                                                 'qualifiers__modifier_name'
            )

            # Create pandas data frame, fill holes with blank strings
            pts_df = pd.DataFrame(list(point_annotations)).fillna('')

            # Rename fields
            point_renames = {
                'image__web_location': 'web_location',
                'label__caab_code': 'caab',
                'label__code_name': 'name',
                'label__cpc_code': 'code',
                'qualifiers__modifier_name': 'modifiers'
            }
            pts_df.rename(columns=point_renames, inplace=True)

            # Group by image and point and aggregate modifiers, then reset indexes
            pts_df = pts_df.groupby(['image_id', 'id']).aggregate({'modifiers': lambda x: ', '.join(x),
                                                              'name': lambda x: x.iat[0],
                                                              'caab': lambda x: x.iat[0],
                                                              'code': lambda x: x.iat[0],
                                                              'label_id': lambda x: x.iat[0],
                                                              }).delevel(['image_id', 'id'])
            pts_df.pop('id')  # remove point ID from output

            # Get counts of common label/modifier combinations and aggregate rows
            rollups = ['name', 'caab', 'code', 'modifiers']
            agg_pts_df = pts_df.groupby(['image_id'] + rollups).label_id.count().unstack(rollups)

            # Sort class columns (transpose columns to rows then re-transpose to rows to columns)
            #agg_pts_df = agg_pts_df.T.sortlevel().T

            if format == "allclasses":
                # Reindex columns to include all classes
                classlist = AnnotationCode.objects.all().order_by('code_name').values_list('code_name',
                                                                                           'caab_code',
                                                                                           'cpc_code')
                classlist = map(lambda t: list(t) + [u''], classlist)  # Add empty modifier
                classlist = pd.MultiIndex.from_tuples(classlist, names=rollups)  # cast to MultiIndex

                # Full list of classes, and modifiers ordered by class
                #agg_pts_df = agg_pts_df.reindex(columns=classlist + agg_pts_df.columns)
                #a = agg_pts_df.reindex(columns=classlist)  # Full list of classes, NO MODIFIERS
                #b = agg_pts_df.reindex(columns=(agg_pts_df.columns + classlist) - classlist)  # ONLY modified classes
                # agg_pts_df.xs(u'', level='modifiers', axis=1)  # Get all the columns WITHOUT modifiers

                # Full list of classes with modifiers tacked on at the end
                agg_pts_df = pd.concat([agg_pts_df.reindex(columns=classlist), # Full list of classes, NO MODIFIERS
                                        agg_pts_df.reindex(columns=(agg_pts_df.columns + classlist) - classlist)], # ONLY modified classes
                                       axis=1)


            # Get list of images with pose information
            images = annotation.collection.images.values('id',
                                                         'web_location',
                                                         'pose__date_time',
                                                         'pose__depth',
                                                         'pose__position')
            # Create pandas data frame and rename columns
            image_df = pd.DataFrame(list(images))
            image_renames = {
                'id': 'image_id',
                'pose__date_time': 'date_time',
                'pose__depth': 'depth',
                'pose__position': 'position'
            }
            image_df.rename(columns=image_renames, inplace=True)

            # Set index
            image_df.set_index('image_id', inplace=True)

            # Convert position to lat and lon
            image_df['latitude'] = image_df.position.apply(lambda p: p[1])
            image_df['longitude'] = image_df.position.apply(lambda p: p[0])
            image_df.pop('position')

            # Join images and point label columns and prepare output
            out_df = image_df.join(agg_pts_df)
            out_df.delevel('image_id', inplace=True)
            out_df.set_index(['image_id', 'web_location', 'date_time', 'latitude', 'longitude', 'depth'], inplace=True)
            out_df.columns = pd.MultiIndex.from_tuples(out_df.columns, names=rollups)







    elif clid:
        collection = Collection.objects.get(pk=clid)
        filename = 'images-%s-%s.csv' % (collection.name, str(datetime.date.today()))
        #images = collection.images.filter(
        #    pose__scientificposemeasurement__measurement_type__normalised_name='altitude').values('id', 'web_location',
        #                                                                                          'pose__date_time',
        #                                                                                          'pose__depth',
        #                                                                                          'pose__position',
        #                                                                                          'pose__scientificposemeasurement__value')
        #images = collection.images.annotate(altitude=Max(
        #    'pose__scientificposemeasurement__value',
        #    pose__scientificposemeasurement__measurement_type__normalised_name='altitude')).values('id', 'web_location',
        #                                  'pose__date_time',
        #                                  'pose__depth',
        #                                  'pose__position',
        #                                  'altitude')
        images = collection.images.values('id',
                                          'web_location',
                                          'pose__date_time',
                                          'pose__depth',
                                          'pose__position')

        # Create pandas data frame and rename columns
        image_df = pd.DataFrame(list(images))
        image_renames = {
            'id': 'image_id',
            'pose__date_time': 'date_time',
            'pose__depth': 'depth',
            'pose__position': 'position'
        }
        image_df.rename(columns=image_renames, inplace=True)

        # Set index
        image_df.set_index('image_id', inplace=True)

        # Convert position to lat and lon
        image_df['latitude'] = image_df.position.apply(lambda p: p[1])
        image_df['longitude'] = image_df.position.apply(lambda p: p[0])
        image_df.pop('position')

        out_df = image_df

        #return render_to_csv_response(images, append_datestamp=True)

    # Prepare response to download as csv mimetype
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s;' % filename
    response['Cache-Control'] = 'no-cache'
    out_df_strbuff = cStringIO.StringIO()
    out_df.to_csv(out_df_strbuff, sep=',')
    out_df_strbuff.reset()
    response.write(out_df_strbuff.read())
    return response


# This view imports classes from a google spreadsheet
# TODO: robustify and make better!!!
def update_classes_gspread(request):
    import gspread
    from annotations.models import AnnotationCode

    guser = request.POST.get('guser')
    gpass = request.POST.get('gpass')
    action = request.GET.get('action')
    field = request.GET.get('field')

    gc = gspread.login(guser, gpass) # Login with your Google account
    ss = gc.open("squidle classes") # Open a worksheet from spreadsheet with one shot

    response = HttpResponse()
    if action == "import":
        # Import new classes from spreadsheet
        # TODO: use headers to determine column numbers
        # 0: CAAB code
        # 1: Class Name
        # 2: CPC/orig code (for reference)
        # 3: Short name
        # 4: Colour
        # 5: Parent CAAB
        wks = ss.worksheet("Valid new classes (read-only)")
        list_of_lists = wks.get_all_values()
        headers = list_of_lists[0]
        response.write("<b>{}</b><br>".format(headers))

        for annotation_list in list_of_lists[1:]:
            try:
                response.write("Adding: {}...".format(annotation_list[1]))
                parentclass = AnnotationCode.objects.filter(caab_code=annotation_list[5])[0]
                newclass = AnnotationCode(caab_code=annotation_list[0], cpc_code=annotation_list[3],
                                          point_colour=annotation_list[4], code_name=annotation_list[1],
                                          description="No description.", parent=parentclass)
                newclass.save()
                response.write("...DONE!<br>")

            except Exception as e:
                response.write("...ERROR!!!!!! {}<br>".format(e.message))

    # TODO: update other fields too (currently only updates colour
    elif action == "update":
        wks = ss.worksheet("Existing classes (read-only)")
        # 0:ID
        # 1:CAAB code
        # 2:Class Name
        # 3:Description
        # 4:Short name
        # 5:Colour
        # 6:Parent ID
        # 7:Parent CAAB
        list_of_lists = wks.get_all_values()
        for annotation_list in list_of_lists[1:]:
            try:
                response.write("Updating: {}...".format(annotation_list[2]))
                thisclass = AnnotationCode.objects.filter(caab_code=annotation_list[1])[0]
                if thisclass.point_colour != annotation_list[8]:
                    response.write("CHANGING FROM: {} to {}".format(thisclass.point_colour, annotation_list[8]))
                    thisclass.point_colour = annotation_list[8]
                    thisclass.save()

                response.write("...DONE!<br>")
            except Exception as e:
                response.write("...ERROR!!!!!! {}<br>".format(e.message))

    elif action == "export":
        wks = ss.worksheet("Existing classes (read-only)")
        allclasses = AnnotationCode.objects.all().order_by('code_name').values_list('id', 'caab_code', 'code_name',
                                                                                    'description', 'cpc_code',
                                                                                    'point_colour', 'parent_id',
                                                                                    'parent__caab_code')
        # Select a cell range
        cell_list = wks.range('A{}:H{}'.format(2, len(allclasses) + 1))
        flat_list = [val for subl in allclasses for val in subl] # flatten class list to enable batch updating

        for i in range(0, len(flat_list), 1):
            cell_list[i].value = flat_list[i]

        # Send update in batch mode
        wks.update_cells(cell_list)
        response.write("Done updating spreadsheet with ALL existing classes<br>")

    return response


    #return render_to_response('webinterface/viewproject.html',
    #      #    return render_to_response('webinterface/viewcollectionalternative.html',
    #      {'clid': clid,
    #       'wsid': wsid,
    #       "asid": asid,
    #       "imid": imid,
    #       "clform": clform,
    #       "wsform": wsform,
    #       "ulwsform": ulwsform,
    #       "asform": asform,
    #       "aform": aform,
    #       "suform": suform,
    #       "GEOSERVER_URL": settings.GEOSERVER_URL},
    #      RequestContext(request))


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


def image_annotate(request, image_id):
    apistring = request.GET.get("apistring", "")
    offset = request.GET.get("offset", "")
    annotation_id = request.GET.get("asid", "")

    return render_to_response('webinterface/imageview.html', #imageannotate.html',
                              {"image_id": image_id, "offset": offset, "apistring": apistring,
                               "annotation_id": annotation_id},
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
def get_extents(request):

    type = request.GET.get('type')
    feature = 'filters'


    #if request.method == 'POST':  # If the form has been submitted...
        # ids = request.POST.get('ids').__str__().split(",")
    ids = request.GET.get('ids').__str__().split(",")

    if feature == 'poses' :
        extent = Pose.objects.filter(deployment_id__in=ids).extent().__str__()
        response_data = {"extent": extent}
    elif feature == 'filters' :
        altitude = ScientificPoseMeasurement.objects.filter(pose__deployment__id__in=ids, measurement_type__normalised_name="altitude")
        depth = Pose.objects.filter(deployment_id__in=ids)
        extent = {'altitude':dict(altitude.aggregate(Min('value')).items() + altitude.aggregate(Max('value')).items()),
                  'depth':dict(depth.aggregate(Min('depth')).items() + depth.aggregate(Max('depth')).items())}
        #print extent
        response_data = extent

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    #return HttpResponse(simplejson.dumps({"message": "GET operation invalid, must use POST."}), mimetype="application/json")

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
    url = request.GET.get('url', None)

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
