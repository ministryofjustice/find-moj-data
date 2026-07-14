from django import forms
from django.forms.widgets import RadioSelect, Textarea, TextInput

from .models import FeedBackNo, FeedBackReport, FeedBackYes, Issue


def formfield(field, **kwargs):
    """
    Wrapper around the db model's formfield method that maps db fields to form fields.

    This is a workaround to prevent a blank choice being included in the ChoiceField.
    By default, if the model field has no default value (or blank is set to True),
    then it will include this empty value, even if we have customised the widget is customised.
    """
    return field.formfield(initial=None, **kwargs)


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["additional_info"]
        widgets = {
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
        label="Would you like an emailed copy of your report?",
        error_messages={"required": "Select if you want us to email you a copy of this report"},
    )


class FeedbackYesForm(forms.ModelForm):
    error_summary_messages = {
        "interested_in_research": "Choose Yes or No to submit",
    }

    something_else = forms.BooleanField(
        required=False,
        label="Something else",
        widget=forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
    )

    what_went_well = forms.CharField(
        required=False,
        label="Tell us what went well",
        widget=Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": "1",
                "aria-describedby": "what-went-well-hint",
                "style": "width: 600px",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interested_in_research"].required = True
        self.fields["interested_in_research"].error_messages = {
            "required": "Choose Yes or No to submit",
            "invalid_choice": "Choose Yes or No to submit",
        }
        self.fields["interested_in_research"].choices = [(True, "Yes"), (False, "No")]
        self.initial["interested_in_research"] = None

    def get_error_summary_items(self):
        summary_errors = []
        ordered_fields = []

        if "__all__" in self.errors:
            ordered_fields.append("__all__")

        ordered_fields.extend(field_name for field_name in self.fields.keys() if field_name in self.errors)

        ordered_fields.extend(field_name for field_name in self.errors.keys() if field_name not in ordered_fields)

        for errored_field in ordered_fields:
            error_messages = self.errors.get(errored_field, [])
            href = "feedback-errors" if errored_field == "__all__" else f"id_{errored_field}"
            for error in error_messages:
                summary_errors.append(
                    {
                        "href": href,
                        "message": self.error_summary_messages.get(errored_field, error),
                    }
                )
        return summary_errors

    error_summary_messages = {
        "interested_in_research": "Choose Yes or No to submit",
    }

    something_else = forms.BooleanField(
        required=False,
        label="Something else",
        widget=forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
    )

    what_went_well = forms.CharField(
        required=False,
        label="Tell us what went well",
        widget=Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": "1",
                "aria-describedby": "what-went-well-hint",
                "style": "width: 600px",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interested_in_research"].required = True
        self.fields["interested_in_research"].error_messages = {
            "required": "Choose Yes or No to submit",
            "invalid_choice": "Choose Yes or No to submit",
        }
        self.fields["interested_in_research"].choices = [(True, "Yes"), (False, "No")]
        self.initial["interested_in_research"] = None

    def get_error_summary_items(self):
        summary_errors = []
        for errored_field, error_messages in self.errors.items():
            href = "feedback-errors" if errored_field == "__all__" else f"id_{errored_field}"
            for error in error_messages:
                summary_errors.append(
                    {
                        "href": href,
                        "message": self.error_summary_messages.get(errored_field, error),
                    }
                )
        return summary_errors

    class Meta:
        model = FeedBackYes
        fields = [
            "easy_to_find",
            "information_useful",
            "information_easy_to_understand",
            "something_else",
            "what_went_well",
            "additional_information",
            "interested_in_research",
            "url_path",
        ]
        widgets = {
            "easy_to_find": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "information_useful": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "information_easy_to_understand": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "something_else": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "5",
                    "aria-describedby": "more-detail-hint",
                    "style": "width: 600px",
                }
            ),
            "url_path": forms.HiddenInput(),
            "interested_in_research": RadioSelect(attrs={"class": "govuk-radios__input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        something_else = cleaned_data.get("something_else")
        what_went_well = (cleaned_data.get("what_went_well") or "").strip()

        if something_else:
            cleaned_data["what_went_well"] = what_went_well
        else:
            cleaned_data["what_went_well"] = ""

        if something_else and not what_went_well:
            self.add_error("what_went_well", "Tell us what went well to continue")

        if not any(
            cleaned_data.get(field)
            for field in [
                "easy_to_find",
                "information_useful",
                "information_easy_to_understand",
                "something_else",
            ]
        ):
            raise forms.ValidationError("Select one or more options to continue")
        return cleaned_data


class FeedbackNoForm(forms.ModelForm):
    error_summary_messages = {
        "interested_in_research": "Choose Yes or No to submit",
    }

    something_else = forms.BooleanField(
        required=False,
        label="Something else",
        widget=forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
    )

    what_went_wrong = forms.CharField(
        required=False,
        label="Tell us what was wrong",
        widget=Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": "1",
                "aria-describedby": "what-went-wrong-hint",
                "style": "width: 600px",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interested_in_research"].required = True
        self.fields["interested_in_research"].error_messages = {
            "required": "Choose Yes or No to submit",
            "invalid_choice": "Choose Yes or No to submit",
        }
        self.fields["interested_in_research"].choices = [(True, "Yes"), (False, "No")]
        self.initial["interested_in_research"] = None

    def get_error_summary_items(self):
        summary_errors = []
        ordered_fields = []

        if "__all__" in self.errors:
            ordered_fields.append("__all__")

        ordered_fields.extend(field_name for field_name in self.fields.keys() if field_name in self.errors)

        ordered_fields.extend(field_name for field_name in self.errors.keys() if field_name not in ordered_fields)

        for errored_field in ordered_fields:
            error_messages = self.errors.get(errored_field, [])
            href = "feedback-errors" if errored_field == "__all__" else f"id_{errored_field}"
            for error in error_messages:
                summary_errors.append(
                    {
                        "href": href,
                        "message": self.error_summary_messages.get(errored_field, error),
                    }
                )
        return summary_errors

    error_summary_messages = {
        "interested_in_research": "Choose Yes or No to submit",
    }

    something_else = forms.BooleanField(
        required=False,
        label="Something else",
        widget=forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
    )

    what_went_wrong = forms.CharField(
        required=False,
        label="Tell us what was wrong",
        widget=Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": "1",
                "aria-describedby": "what-went-wrong-hint",
                "style": "width: 600px",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interested_in_research"].required = True
        self.fields["interested_in_research"].error_messages = {
            "required": "Choose Yes or No to submit",
            "invalid_choice": "Choose Yes or No to submit",
        }
        self.fields["interested_in_research"].choices = [(True, "Yes"), (False, "No")]
        self.initial["interested_in_research"] = None

    def get_error_summary_items(self):
        summary_errors = []
        for errored_field, error_messages in self.errors.items():
            href = "feedback-errors" if errored_field == "__all__" else f"id_{errored_field}"
            for error in error_messages:
                summary_errors.append(
                    {
                        "href": href,
                        "message": self.error_summary_messages.get(errored_field, error),
                    }
                )
        return summary_errors

    class Meta:
        model = FeedBackNo
        fields = [
            "not_clear",
            "information_not_available",
            "incomplete_information",
            "difficult_to_understand",
            "something_else",
            "what_went_wrong",
            "additional_information",
            "interested_in_research",
            "url_path",
        ]
        widgets = {
            "not_clear": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "information_not_available": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "incomplete_information": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "difficult_to_understand": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "something_else": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "5",
                    "aria-describedby": "more-detail-hint",
                    "style": "width: 600px",
                }
            ),
            "url_path": forms.HiddenInput(),
            "interested_in_research": RadioSelect(attrs={"class": "govuk-radios__input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        something_else = cleaned_data.get("something_else")
        what_went_wrong = (cleaned_data.get("what_went_wrong") or "").strip()

        if something_else:
            cleaned_data["what_went_wrong"] = what_went_wrong
        else:
            cleaned_data["what_went_wrong"] = ""

        if something_else and not what_went_wrong:
            self.add_error("what_went_wrong", "Tell us what was wrong to continue")

        if not any(
            cleaned_data.get(field)
            for field in [
                "not_clear",
                "information_not_available",
                "incomplete_information",
                "difficult_to_understand",
                "something_else",
            ]
        ):
            raise forms.ValidationError("Select one or more options to continue")
        return cleaned_data


class FeedbackReportForm(forms.ModelForm):
    class Meta:
        model = FeedBackReport
        fields = [
            "not_working",
            "needs_fixing",
            "something_else",
            "additional_information",
            "url_path",
        ]
        widgets = {
            "not_working": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "needs_fixing": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "something_else": forms.CheckboxInput(attrs={"class": "govuk-checkboxes__input"}),
            "additional_information": Textarea(
                attrs={
                    "class": "govuk-textarea",
                    "rows": "5",
                    "aria-describedby": "more-detail-hint",
                    "style": "width: 600px",
                }
            ),
            "url_path": forms.HiddenInput(),
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
            raise forms.ValidationError("Select one or more options to continue")
        return cleaned_data
