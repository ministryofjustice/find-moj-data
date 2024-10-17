from django import forms
from django.forms.widgets import RadioSelect, Textarea, TextInput

from .models import Feedback, ReportIssue


def formfield(field, **kwargs):
    """
    Wrapper around the db model's formfield method that maps db fields to form fields.

    This is a workaround to prevent a blank choice being included in the ChoiceField.
    By default, if the model field has no default value (or blank is set to True),
    then it will include this empty value, even if we have customised the widget is customised.
    """
    return field.formfield(initial=None, **kwargs)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["satisfaction_rating", "how_can_we_improve"]
        widgets = {
            "satisfaction_rating": RadioSelect(attrs={"class": "govuk-radios__input"})
        }
        formfield_callback = formfield


class ReportIssueForm(forms.ModelForm):
    class Meta:
        model = ReportIssue
        fields = [
            "reason",
            "additional_info",
            "user_email",
        ]
        widgets = {
            "reason": RadioSelect(attrs={"class": "govuk-radios__input"}),
            "additional_info": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "5",
                    "aria-describedby": "more-detail-hint",
                }
            ),
            "user_email": TextInput(
                attrs={
                    "class": "govuk-input",
                    "type": "email",
                    "spellcheck": "false",
                    "aria-describedby": "email-hint",
                    "autocomplete": "email",
                }
            ),
        }
        formfield_callback = formfield
