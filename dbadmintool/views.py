"""Views for the administratorbot"""
# Create your views here.
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render_to_response
from django.template import RequestContext
import dbadmintool
import dbadmintool.administratorbot as administratorbot
import simplejson
from dbadmintool.models import DataLogger


def stats_views(request):
    """@brief Root html for Catami data

    """

    #db_report_bot = administratorbot.ReportTools()
    #stat_dictionary = db_report_bot.get_stats()
    #stat_dictionary = simplejson.dumps(stat_dictionary)

    stat_dictionary = []
    stat_dictionary.append(['Date', 'num_campaigns', 'num_deployments'])

    for item in Data_logger.objects.all():
        stat_dictionary.append([item.collection_time, item.num_campaigns, item
        .num_deployments])

    stat_dictionary = simplejson.dumps(stat_dictionary, cls=DjangoJSONEncoder)
    # serializers.serialize("json", stat_dictionary)


    return render_to_response(
        'dbadmintool/stats.html',
        {'stat_dictionary': stat_dictionary},
        RequestContext(request))
