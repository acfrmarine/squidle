from django import forms
from annotations.models import POINT_METHODOLOGIES
from annotations.models import PointAnnotationSet, PointAnnotationSetManager
from collection.models import Collection, CollectionManager

#class CreateCollectionForm(forms.Form):
#    collection_name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
#    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Longer description (optional)'}))
#    #deployment_ids = forms.CharField(label=u'Deployments', required=False, widget=forms.SelectMultiple())
#    deployment_ids = forms.CharField(label=u'Deployments', widget=forms.SelectMultiple())

class CreateCollectionForm(forms.Form):
    name = forms.CharField(label=u'Name',widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Longer description (optional)'}))
    deployment_list = forms.CharField(widget=forms.HiddenInput(), required=False)
    depth_range = forms.CharField(widget=forms.HiddenInput(), required=False)
    altitude_range = forms.CharField(widget=forms.HiddenInput(), required=False)
    bounding_boxes = forms.CharField(widget=forms.HiddenInput(), required=False)
    date_time_range = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Method to save input from form
    def save(form, user):
        args = dict()
        args["user"] = user
        for key in form.base_fields:                # arguments to func are same as form fields
            args[key] = form.cleaned_data.get(key)
        return CollectionManager().create_collection(**args)


class CreateWorksetFromImagelist (forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Longer description (optional)'}))
    img_list = forms.CharField(label=u'Image List', widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'List of image names...'}))
    c_id = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    ispublic = forms.IntegerField(widget=forms.HiddenInput(), initial="", required=False)

    # Method to save input from form
    def save(form, user):
        args = dict()
        args["user"] = user
        args["method"] = "upload"
        for key in form.base_fields:                # arguments to func are same as form fields
            args[key] = form.cleaned_data.get(key)
        return CollectionManager().create_workset(**args)


class CreateWorksetFromCPCImport(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Longer description (optional)'}))
    c_id = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    ispublic = forms.IntegerField(widget=forms.HiddenInput(), initial="", required=False)
    cpc_zip = forms.FileField()
    cpc2labelid_csv = forms.FileField()

    # Method to save input from form
    def save(self, user):
        args = dict()
        args["user"] = user
        args["method"] = "cpcimport"

        for key in self.base_fields:                # arguments to func are same as form fields
            args[key] = self.cleaned_data.get(key)

        #TODO: Make sure we have appropriate arguments for the create_workset method.
        return CollectionManager().create_workset(**args)






class CreateWorksetForm(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    #ispublic = forms.BooleanField(label=u'Make public?', required=False)
    method = forms.ChoiceField(label=u'Sub-sample', choices=(('random', 'N random images'),('stratified','Every Nth image'),('grts','N images sampled using GRTS')), initial='random', help_text=u'The method used to subsample the images...')
    n = forms.IntegerField(label=u'N', min_value=1, help_text=u'Number of images or spacing between images (depends on sub-sample method)')
    #start_ind = forms.IntegerField(label=u'Start Index', min_value=0)
    #stop_ind = forms.IntegerField(label=u'Stop Index', min_value=0)
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Longer description (optional)'}))
    #method = forms.CharField(widget=forms.HiddenInput())
    c_id = forms.IntegerField(widget=forms.HiddenInput())
    ispublic = forms.IntegerField(widget=forms.HiddenInput(), initial="", required=False)

    method.widget.attrs["onchange"] = "if ($(this).val() == 'grts') alert('NOTE: the GRTS sample method is still experimental and may not work properly!');"

    # Method to save input from form
    def save(form, user):
        args = dict()
        args["user"] = user
        for key in form.base_fields:                # arguments to func are same as form fields
            args[key] = form.cleaned_data.get(key)
        return CollectionManager().create_workset(**args)



# class CreatePointAnnotationSet (forms.Form):
#     collection = forms.IntegerField(widget=forms.HiddenInput())
#     owner = forms.CharField(widget=forms.HiddenInput())
#     name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
#     methodology = forms.ChoiceField(label=u'Methodology', choices=POINT_METHODOLOGIES, initial=0, help_text=u'The method for positioning the points')
#     count = forms.IntegerField(label=u'N', min_value=1, help_text=u'Number of points')
#
#     # Attach javascript onchange event to select
#     #methodology.widget.attrs["onchange"] = "if ($(this).val() == 3) $(this.form.id_count).val(9)[0].disabled=true;"\
#     #"else if ($(this).val() == 1 || $(this).val() == 2) $(this.form.id_count).val(10)[0].disabled=false;"\
#     #"else  $(this.form.id_count).val(50)[0].disabled=false;"
#     methodology.widget.attrs["onchange"] = "if ($(this).val() == 3) $(this.form.id_count).val(9);" \
#                                            "else if ($(this).val() == 1 || $(this).val() == 2) $(this.form.id_count).val(10);" \
#                                            "else  $(this.form.id_count).val(50);"

class CreatePointAnnotationSet (forms.Form):
    #user, name, methodology, n, c_id
    c_id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    methodology = forms.ChoiceField(label=u'Methodology', choices=POINT_METHODOLOGIES, initial=0, help_text=u'The method for positioning the points')
    n = forms.IntegerField(label=u'N', min_value=1, initial=50, help_text=u'Number of points')

    # Attach javascript onchange event to select
    #methodology.widget.attrs["onchange"] = "if ($(this).val() == 3) $(this.form.id_count).val(9)[0].disabled=true;"\
    #"else if ($(this).val() == 1 || $(this).val() == 2) $(this.form.id_count).val(10)[0].disabled=false;"\
    #"else  $(this.form.id_count).val(50)[0].disabled=false;"
    methodology.widget.attrs["onchange"] = "if ($(this).val() == 3) $(this.form.id_n).attr('disabled','disabled').val('9');" \
                                           "else if ($(this).val() == 1 || $(this).val() == 2) $(this.form.id_n).removeAttr('disabled').val('10');" \
                                           "else  $(this.form.id_n).removeAttr('disabled').val('50');"
    def save (form, user):
        args = dict()
        args["user"] = user
        for key in form.base_fields:                # arguments to func are same as form fields
            args[key] = form.cleaned_data.get(key)
        return PointAnnotationSetManager().create_annotation_set(**args)


class CreateCollectionExploreForm(forms.Form):
    deployment_ids = forms.CharField()
    collection_name = forms.CharField()
    depth__gte = forms.CharField()
    depth__lte = forms.CharField()
    temperature__gte = forms.CharField()
    temperature__lte = forms.CharField()
    salinity__gte = forms.CharField()
    salinity__lte = forms.CharField()
    altitude__gte = forms.CharField()
    altitude__lte = forms.CharField()

#class CreateWorksetForm(forms.Form):
#    name = forms.CharField()
#    description = forms.CharField(required=False)
#    ispublic = forms.BooleanField(required=False)
#    c_id = forms.IntegerField()
#    n = forms.IntegerField()

class CreateWorksetAndAnnotation(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'placeholder': 'Enter a descriptive name'}))
    #ispublic = forms.BooleanField(label=u'Make public?', required=False)
    method = forms.ChoiceField(label=u'Sub-sample', choices=(('random','N random images'),('stratified','Every Nth image')), initial='random')
    n = forms.IntegerField(label=u'N images', min_value=1)
    methodology = forms.ChoiceField(label=u'Annotation method', choices=POINT_METHODOLOGIES, initial=0)
    #methodology = forms.ChoiceField(label=u'Image points', choices=(0,'Random'), initial=0)
    count = forms.IntegerField(label=u'# points', min_value=1)
    description = forms.CharField(label=u'Description', required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Longer description (optional)'}))
    owner = forms.CharField(widget=forms.HiddenInput())
    c_id = forms.IntegerField(widget=forms.HiddenInput())



    #class CreatePointAnnotationSet (forms.ModelForm):
#    class Meta:
#        model = PointAnnotationSet


dataset_forms = {
    "wsform": CreateWorksetForm,
    "clform": CreateCollectionForm,
    "asform": CreatePointAnnotationSet,
    "ulwsform": CreateWorksetFromImagelist,
    "cpcform": CreateWorksetFromCPCImport
}