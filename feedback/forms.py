from django import forms
from django.forms.widgets import RadioSelect, Textarea, TextInput

from .models import Feedback, FeedBackNo, FeedBackReport, FeedbackYes, Issue


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
        error_messages = {
            "satisfaction_rating": {
                "required": "Select how satisfied are you with this service"
            }
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["reason", "additional_info"]
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
        error_messages = {
            "reason": {"required": "Select what is wrong with this page"},
            "additional_info": {"required": "Enter more details about the issue"},
        }

    send_email_to_reporter = forms.TypedChoiceField(
        widget=RadioSelect(
            attrs={"class": "govuk-radios__input", "required": "True"},
        ),
        choices=(("Yes", "Yes"), ("No", "No")),
        coerce=lambda x: x == "Yes",
        required=True,
        label="Would you like us to email you a copy of this report?",
        error_messages={
            "required": "Select if you want us to email you a copy of this report"
        },
    )


class FeedbackYesForm(forms.ModelForm):

    class Meta:
        model = FeedbackYes
        fields = [
            "easy_to_find",
            "information_useful",
            "information_easy_to_understand",
            "interested_in_research",
            "additional_information",
            "url_path",
        ]
        widgets = {
            "easy_to_find": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "information_useful": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "information_easy_to_understand": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "3",
                    "aria-describedby": "more-detail-hint",
                }
            ),
            "url_path": forms.HiddenInput(),
            "interested_in_research": RadioSelect(
                attrs={"class": "govuk-radios__input"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any(
            cleaned_data.get(field)
            for field in [
                "easy_to_find",
                "information_useful",
                "information_easy_to_understand",
                "additional_information",
            ]
        ):
            raise forms.ValidationError("Select at least one option or provide details")
        return cleaned_data


class FeedbackNoForm(forms.ModelForm):

    class Meta:
        model = FeedBackNo
        fields = [
            "not_clear",
            "information_not_available",
            "incomplete_information",
            "difficult_to_understand",
            "interested_in_research",
            "additional_information",
            "url_path",
        ]
        widgets = {
            "not_clear": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "information_not_available": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "incomplete_information": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "difficult_to_understand": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "3",
                    "aria-describedby": "more-detail-hint",
                }
            ),
            "url_path": forms.HiddenInput(),
            "interested_in_research": RadioSelect(
                attrs={"class": "govuk-radios__input"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any(
            cleaned_data.get(field)
            for field in [
                "not_clear",
                "information_not_available",
                "incomplete_information",
                "difficult_to_understand",
                "additional_information",
            ]
        ):
            raise forms.ValidationError("Select at least one option or provide details")
        return cleaned_data


class FeedbackReportForm(forms.ModelForm):

    class Meta:
        model = FeedBackReport
        fields = [
            "not_working",
            "needs_fixing",
            "something_else",
            "interested_in_research",
            "additional_information",
            "url_path",
        ]
        widgets = {
            "not_working": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "needs_fixing": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "something_else": forms.CheckboxInput(
                attrs={"class": "govuk-checkboxes__input"}
            ),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "3",
                    "aria-describedby": "more-detail-hint",
                }
            ),
            "url_path": forms.HiddenInput(),
            "interested_in_research": RadioSelect(
                attrs={"class": "govuk-radios__input"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any(
            cleaned_data.get(field)
            for field in [
                "not_working",
                "needs_fixing",
                "something_else",
                "additional_information",
            ]
        ):
            raise forms.ValidationError("Select at least one option or provide details")
        return cleaned_data
