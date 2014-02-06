"""Views for the staging app.
"""

from django.template import RequestContext

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse

from catamidb import authorization
from .api import StagingFilesResource

from .forms import CampaignCreateForm, ApiDeploymentForm
import os.path

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import logging

logger = logging.getLogger(__name__)

@login_required
def newbrowse(request):
    context = {}
    rcon = RequestContext(request)

    sf = StagingFilesResource()
    sf_bundle = sf.build_bundle(request=request)

    context['current_files'] = sf.obj_get_list(sf_bundle)

    return render_to_response('staging/newbrowse.html', context, rcon)


def api_auv_form(request, pk):
    context = {}
    rcon = RequestContext(request)

    context['form'] = ApiDeploymentForm()
    context['pk'] = pk
    context['resource_name'] = 'stagingfiles'
    context['api_name'] = 'dev'

    return render_to_response('staging/api_deployment_create.html', context,
                              rcon)


@login_required
def index(request):
    """The home/index view for staging."""
    context = {}

    rcon = RequestContext(request)

    return render_to_response('staging/index.html', context, rcon)


@login_required
def campaigncreate(request):
    context = {}

    if request.method == 'POST':
        form = CampaignCreateForm(request.POST)

        if form.is_valid():
            campaign = form.save()

            return redirect('staging.views.campaigncreated')
    else:
        form = CampaignCreateForm()

    rcon = RequestContext(request)
    context['form'] = form

    return render_to_response('staging/campaigncreate.html', context, rcon)

@login_required
def campaigncreated(request):
    """Displays the thankyou message on campaigncreate success."""
    context = {}
    rcon = RequestContext(request)

    return render_to_response('staging/campaigncreated.html', context, rcon)


# to enable the handler to exist...
@login_required
@csrf_exempt
def fileupload(request):
    """Handles setting up progress handler and uploading json files."""
    # get a new progress
    #key = Progress.objects.get_new()


    # this is done here due to issues with csrf and touching of the POST
    # data
    request.upload_handlers.insert(0, UploadProgressCachedHandler(request))
    return _fileupload(request)


@csrf_protect
def _fileupload(request):
    """Deals with the actual uploading of files."""
    context = {}
    rcon = RequestContext(request)

    if request.method == 'POST':
        form = FileImportForm(request.POST, request.FILES)

        if form.is_valid():
            # this is where the import is performed...
            # and the file is read in
            logger.debug("_fileupload: getting uploaded file.")
            upload = request.FILES['upload_file']

            # if it is large, read from the file
            # else read the entirety into a string
            try:
                if hasattr(upload, 'temporary_file_path'):
                    logger.debug(
                        "_fileupload: large file so pass filename to json_fload.")
                    tasks.json_fload(upload.temporary_file_path())
                else:
                    logger.debug(
                        "_fileupload: small file so pass string to json_sload.")
                    tasks.json_sload(upload.read())

            except Exception as exc:
                errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                                 forms.util.ErrorList())
                errors.append("{0}: {1}".format(exc.__class__.__name__, exc))
                logger.debug(
                    '_fileupload: failed to import json contents: ({0}): {1}'.format(
                        exc.__class__.__name__, exc))
            else:
                logger.debug(
                    "_fileupload: import successful, redirecting to fileuploaded.")
                return redirect('staging.views.fileuploaded')
    else:
        form = FileImportForm()

    context['form'] = form

    return render_to_response('staging/fileupload.html', context, rcon)


@login_required
def fileuploaded(request):
    """Thankyou message after uploaded file imported successfully."""
    context = {}
    rcon = RequestContext(request)

    return render_to_response('staging/fileuploaded.html', context, rcon)


@login_required
def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson

        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError(
            'Server Error: You must provide X-Progress-ID header or query param.')

