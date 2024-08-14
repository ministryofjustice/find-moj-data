from django.forms import ModelForm
from django.forms.widgets import RadioSelect

from .models import Feedback


def formfield(field, **kwargs):
    """
    Wrapper around the db model's formfield method that maps db fields to form fields.

    This is a workaround to prevent a blank choice being included in the ChoiceField.
    By default, if the model field has no default value (or blank is set to True),
    then it will include this empty value, even if we have customised the widget is customised.
    """
    return field.formfield(initial=None, **kwargs)


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ["satisfaction_rating", "how_can_we_improve"]
        widgets = {
            "satisfaction_rating": RadioSelect(attrs={"class": "govuk-radios__input"})
        }
        formfield_callback = formfield
