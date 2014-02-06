from django import forms
from django.db import models
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('complete', 'request_date')

class FeedbackEditForm(forms.ModelForm):
    class Meta:
        model = Feedback
