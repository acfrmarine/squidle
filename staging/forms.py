"""Forms for the staging application.

This includes AUVImportForm and FileImportForm.
"""
from django import forms

from catamidb.models import Campaign

import logging

logger = logging.getLogger(__name__)

class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign


class FileImportForm(forms.Form):
    """Form to assist with uploading a json file.

    Particularly targetted at files to directly deserialize.
    """
    upload_file = forms.FileField()

    upload_file.help_text = "JSON file in import format."

class ApiDeploymentForm(forms.Form):
    short_name = forms.CharField()
    campaign = forms.ModelChoiceField(queryset=Campaign.objects.all())
    license = forms.CharField(max_length=500)
    descriptive_keywords = forms.CharField(max_length=500)

    def clean_short_name(self):
        """Perform extra cleaning on the field.

        In this case strip non valid characters from the name. Mainly
        the slash, and backslash.
        """

        # get the existing value
        sn = self.cleaned_data['short_name']

        # remove the characters
        # this is a unicode string, so the mapping is a little more
        # complicated
        sn = sn.translate({ord(u'/'):None, ord(u'\\'):None})

        # and return the newly recleaned value
        return sn

