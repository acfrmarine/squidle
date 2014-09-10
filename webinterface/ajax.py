from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
import guardian
from webinterface.forms import dataset_forms, CreateCollectionForm, CreateWorksetForm, CreateWorksetFromImagelist
from collection.models import Collection, CollectionManager

from django.contrib.auth import authenticate, login, logout
from userena.forms import AuthenticationForm, SignupForm
from userena import settings as userena_settings

@dajaxice_register
def signin_form(request, form):
    dajax = Dajax()
    form = AuthenticationForm(deserialize_form(form))
    form_id = '#aform'

    try:
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))
        if not form.is_valid():
            raise Exception('Error')

        identification, password, remember_me = (form.cleaned_data['identification'],
                                                 form.cleaned_data['password'],
                                                 form.cleaned_data['remember_me'])
        user = authenticate(identification=identification, password=password)
        if user.is_active:
            login(request, user)
            if remember_me:
                request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
            else:
                request.session.set_expiry(0)

            dajax.script('update_sign_in({0},"{1}");'.format(user.id,user.username))
    except Exception as e:
        dajax.remove_css_class(form_id+' input', 'error')
        print e
        dajax.script("form_errors(true,'{0}','{1}<br>{2}');".format(form_id,e.message,form.errors))
        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    return dajax.json()

@dajaxice_register
def signup_form(request, form):
    dajax = Dajax()
    form = SignupForm(deserialize_form(form))
    form_id = '#suform'

    try:
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))
        if not form.is_valid():
            raise Exception('Processing error')

        form.full_clean()
        identification, password = (form.cleaned_data['username'], form.cleaned_data['password1'])
        #identification, password = (user.username, user.password)

        form.save()
        user = authenticate(identification=identification, password=password)
        if user.is_active:
            print "Authenticated!!!"
            login(request, user)
            dajax.script('update_sign_in({0},"{1}");'.format(user.id,user.username))

    except Exception as e:
        dajax.remove_css_class(form_id+' input', 'error')
        print e
        dajax.script("form_errors(true,'{0}','{1}:<br>{2}');".format(form_id,e.message,form.errors))


        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    print dajax.json()

    return dajax.json()


@dajaxice_register
def save_new_dataset (request, form_data, form_id):
    dajax = Dajax()

    form = dataset_forms[form_id](deserialize_form(form_data))

    if form.is_valid():  # All validation rules pass
        id, msg = form.save(request.user)
        if id is None: id = "null"
        dajax.script('update_dataset_form("{}", "success", "{}", {});'.format(form_id, msg, id))
    else:
        dajax.script('update_dataset_form("{}", "formerror", "Please correct/complete the fields highlighted in red",null);'.format(form_id))
        for error in form.errors:
            dajax.add_css_class('#'+form_id+' #id_%s' % error, 'error')

    return dajax.json()


@dajaxice_register
def send_workset_form(request, form, form_id):
    dajax = Dajax()
    form = CreateWorksetForm(deserialize_form(form))
    user = request.user
    #if request.user.is_anonymous():
    #    user = guardian.utils.get_anonymous_user()

    #print form

    if form.is_valid():  # All validation rules pass
        print "VALID!"
        #dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        wsid, msg = CollectionManager().create_workset(
            user,
            form.cleaned_data.get('name'),
            form.cleaned_data.get('description'),
            form.cleaned_data.get('ispublic') == "true",
            int(form.cleaned_data.get('c_id')),
            form.cleaned_data.get('method'),
            n=int(form.cleaned_data.get('n'))#,
            #start_ind=0, #int(form.cleaned_data.get('start_ind')),
            #stop_ind=0  #int(form.cleaned_data.get('stop_ind'))
        )

        if wsid is None: wsid = "null"
        #dajax.script('refresh_datasets("wsid","{0}",{1},"{2}", "#new-annotationset-modal");'.format(form_id,wsid,msg))
        dajax.script('update_dataset_form({}, "wsid", "{}," {});'.format(form_id, msg, wsid))
    else:
        print "NOT VALID!"
        #print form.errors
        #dajax.remove_css_class(form_id+' input', 'error')
        #dajax.script('form_errors(true,"{0}");'.format(form_id))
        print form_id
        #dajax.script("form_errors(true,'{}','Please correct the errors in red below');".format(form_id))
        #dajax.script('update_dataset_form({}, "error", {});'.format(form_id, form.errors))
        dajax.script('update_dataset_form("{}", "error", "Please correct/complete the fields highlighted in red",0);'.format(form_id))
        for error in form.errors:
            dajax.add_css_class('#'+form_id+' #id_%s' % error, 'error')

    print "COMPLETE!"

    return dajax.json()





@dajaxice_register
def send_workset_imagelist_form(request, form, form_id):
    dajax = Dajax()
    form = CreateWorksetFromImagelist(deserialize_form(form))

    user = request.user
    #if request.user.is_anonymous():
    #    user = guardian.utils.get_anonymous_user()

    print form.cleaned_data.get()
    if form.is_valid():  # All validation rules pass
        dajax.remove_css_class(form_id + ' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        # Split image list by lines and commas and strip white space
        #img_list = form.cleaned_data.get('imglist').replace(',', '\n').splitlines()
        img_list = [line.strip() for line in form.cleaned_data.get('imglist').replace(',', '\n').splitlines() if line.strip()]

        wsid, msg = CollectionManager().create_workset(
            user,
            form.cleaned_data.get('name'),
            form.cleaned_data.get('description'),
            form.cleaned_data.get('ispublic') == "true",
            int(form.cleaned_data.get('c_id')),
            "upload",
            img_list=img_list
        )

        if wsid is None: wsid = "null"
        dajax.script('refresh_datasets("wsid","{0}",{1},"{2}", "#new-annotationset-modal");'.format(form_id, wsid, msg))

    else:
        dajax.remove_css_class(form_id + ' input', 'error')
        #dajax.script('form_errors(true,"{0}");'.format(form_id))
        dajax.script("form_errors(true,'{0}','{1}');".format(form_id, form.errors))
        for error in form.errors:
            dajax.add_css_class(form_id + ' #id_%s' % error, 'error')

    return dajax.json()

@dajaxice_register
def send_collection_form(request, form, form_id):
    dajax = Dajax()
    form = CreateCollectionForm(deserialize_form(form))
    #print form

    user = request.user
    #if request.user.is_anonymous():
    #    user = guardian.utils.get_anonymous_user()


    if form.is_valid():  # All validation rules pass
        dajax.remove_css_class(form_id+' input', 'error')
        dajax.script('form_errors(false,"{0}");'.format(form_id))

        #import pdb
        #pdb.set_trace()

        formdata = form.cleaned_data

        #print form.data.getlist('deployment_ids')
        name = formdata.get('collection_name')
        description = formdata.get('description')
        deployment_ids = [int(x) for x in formdata.get('deployment_ids').split(',')] if formdata.get('deployment_ids') else None
        depth = [float(x) for x in formdata.get('depth').split(',')] if formdata.get('depth') else None
        altitude = [float(x) for x in formdata.get('altitude').split(',')] if formdata.get('altitude') else None
        bboxes = formdata.get('bboxes').split(':') if formdata.get('bboxes') else None
        date_time = formdata.get('date_time').split(',') if formdata.get('date_time') else None

        clid, msg=CollectionManager().create_collection(user,name,description,deployment_ids,depth,altitude,bboxes,date_time)

        if clid is None: clid = "null"
        dajax.script('refresh_datasets("clid","{0}",{1},"{2}", "#new-workset-modal");'.format(form_id,clid,msg))
    else:
        dajax.remove_css_class(form_id+' input', 'error')
        #dajax.script('form_errors(true,"{0}");'.format(form_id))
        dajax.script("form_errors(true,'{0}','{1}');".format(form_id,form.errors))
        for error in form.errors:
            dajax.add_css_class(form_id+' #id_%s' % error, 'error')

    return dajax.json()
