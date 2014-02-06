from django.forms.fields import FileField
from django.forms.widgets import FileInput


class MultiFileInput(FileInput):
    def render(self, name, value, attrs=None):
        base = attrs or {}
        attrs = dict(base)
        attrs['multiple'] = "multiple"

        return super(MultiFileInput, self).render(name, None, attrs=attrs)


class MultiFileField(FileField):
    widget = MultiFileInput
