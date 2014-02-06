"""@brief Django views generation (html) for Catami (top level).

Created Mark Gray 10/09/2012
markg@ivec.org

Edits :: Name : Date : description

"""
# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import logout
from Force.models import AUVDeployment, BRUVDeployment, DOVDeployment, TIDeployment, TVDeployment, Deployment, Image
import httplib2
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

#@login_required
def index(request):
    """@brief returns root catami html

    """

    recent_deployments = Deployment.objects.all().order_by('-id')[:3]
    random_images = Image.objects.all().order_by('?')[:9]

    styled_deployment_list = []
    image_link_list = []

    for image in random_images:
        try:
            AUVDeployment.objects.get(id=image.deployment.id)
        except:
            pass
        else:
            image_link = {"deployment_url": "/data/auvdeployments/" + str(image.deployment.id), "image": image}

        try:
            TIDeployment.objects.get(id=image.deployment.id)
        except:
            pass
        else:
            image_link = {"deployment_url": "/data/tideployments/" + str(image.deployment.id), "image": image}

        image_link_list.append(image_link)

    for deployment in recent_deployments:
        try:
            AUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type = "AUV Deployment"
            deployment_url = "/data/auvdeployments/" + str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type = "BRUV Deployment"
            deployment_url = "/data/bruvdeployments/" + str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type = "DOV Deployment"
            deployment_url = "/data/dovdeployments/" + str(deployment.id)

        try:
            TIDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type = "TI Deployment"
            deployment_url = "/data/tideployments/" + str(deployment.id)

        try:
            BRUVDeployment.objects.get(id=deployment.id)
        except:
            pass
        else:
            deployment_type = "TV Deployment"
            deployment_url = "/data/tvdeployments/" + str(deployment.id)

        styled_deployment = {"deployment_type": deployment_type, "deployment_url": deployment_url,
                             "deployment": deployment}
        styled_deployment_list.append(styled_deployment)

    return render_to_response('catamiPortal/index.html',
                              {'styled_deployment_list': styled_deployment_list,
                               'image_link_list': image_link_list},
                              RequestContext(request))


def faq(request):
    """@brief returns catami faq html

    """
    context = {}

    return render_to_response('catamiPortal/faq.html',
                              context,
                              RequestContext(request))


def contact(request):
    """@brief returns catami contact html

    """
    context = {}

    return render_to_response('catamiPortal/contact.html',
                              context,
                              RequestContext(request))


def attribution(request):
    """@brief returns catami atribution html"""

    context = {}

    return render_to_response('catamiPortal/attribution.html',
                              context,
                              RequestContext(request))


def logout_view(request):
    """@brief returns user to html calling the logout action

    """
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@csrf_exempt
def proxy(request, url):
    conn = httplib2.Http()
    if request.method == "GET":
        #url_ending = "%s?%s" % (url, urlencode(request.GET))
        #url = url_ending
        #url = (url, urlencode(request.GET))
        resp, content = conn.request(url, request.method)
        return HttpResponse(content)
    elif request.method == "POST":
        url = url
        #data = urlencode(request.POST)
        data = request.body
        resp, content = conn.request(url, request.method, data)
        return HttpResponse(content)
