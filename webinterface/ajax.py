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
    form_id = 'aform'

    try:
        dajax.remove_css_class('#'+form_id+' input', 'error')
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
        dajax.remove_css_class('#'+form_id+' input', 'error')
        print e
        dajax.script("form_errors(true,'{0}','{1}<br>{2}');".format(form_id,e.message,form.errors))
        for error in form.errors:
            dajax.add_css_class('#'+form_id+' #id_%s' % error, 'error')

    return dajax.json()

@dajaxice_register
def signup_form(request, form):
    dajax = Dajax()
    form = SignupForm(deserialize_form(form))
    form_id = 'suform'

    try:
        dajax.remove_css_class('#'+form_id+' input', 'error')
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
        dajax.remove_css_class('#'+form_id+' input', 'error')
        print e
        dajax.script("form_errors(true,'{0}','{1}:<br>{2}');".format(form_id,e.message,form.errors))


        for error in form.errors:
            dajax.add_css_class('#'+form_id+' #id_%s' % error, 'error')

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


