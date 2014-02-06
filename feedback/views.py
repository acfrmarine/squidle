from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.core.mail import send_mail

from .models import Feedback

from .forms import FeedbackForm, FeedbackEditForm

import datetime


def add(request):
    context = {}

    if request.method == 'POST':
        feedback = Feedback(request_date=datetime.datetime.now(), complete=False)
        form = FeedbackForm(request.POST, instance=feature)

        if form.is_valid():
            form.save()

            subject = "[webmesh] Feedback Requested: {0}".format(feedback.brief_description)
            contents = "Outline: {1}\nPriority: {0}\n\n{2}".format(
                feedback.priority, 
                feedback.brief_description,
                feedback.full_description,
                )

            send_mail(subject, contents, 'automaton@archipelago.acfr.usyd.edu.au', ['l.toohey@acfr.usyd.edu.au'])
            
            return redirect('feedback.views.request_list')
    else:
        feedback = Feedback(priority=0)
        form = FeedbackForm(instance=feature)

    rcon = RequestContext(request)
    context['form'] = form

    return render_to_response('feedback/add.html', context, rcon)

def request_list(request):
    context = {}
    rcon = RequestContext(request)

    feedback_list = list(Feedback.objects.filter(complete=False))
    feedback_list.sort(key=lambda x: (x.priority, x.request_date))
    context['feedback_list'] = feedback_list

    return render_to_response('feedback/list.html', context, rcon)

def edit(request, pk):
    context = {}

    if request.method == 'POST':
        form = FeedbackEditForm(request.POST, instance=Feedback.objects.get(pk=pk))

        if form.is_valid():
            form.save()
            return redirect('feedback.views.request_list')
    else:
        form = FeedbackEditForm(instance=Feedback.objects.get(pk=pk))

    rcon = RequestContext(request)
    context['form'] = form

    return render_to_response('feedback/edit.html', context, rcon)

def view(request, pk):
    context = {}
    rcon = RequestContext(request)

    feedback = get_object_or_404(Feedback, pk=pk)

    context['feedback'] = feedback

    return render_to_response('feedback/view.html', context, rcon)

def delete(request, pk):
    context = {}
    rcon = RequestContext(request)

    feedback = get_object_or_404(Feedback, pk=pk)

    feedback.delete()
    
    return redirect('feedback.views.request_list')
