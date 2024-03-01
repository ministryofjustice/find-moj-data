from copy import deepcopy
from urllib.parse import urlencode

from django import forms

from .domain_model import Domain, DomainModel


def get_domain_choices() -> list[Domain]:
    """Make API call to obtain domain choices"""
    choices = [
        Domain("", "All domains"),
    ]
    choices.extend(DomainModel().top_level_domains)
    return choices


def get_subdomain_choices() -> list[Domain]:
    choices = [Domain("", "All subdomains")]
    choices.extend(DomainModel().all_subdomains())
    return choices


def get_sort_choices():
    return [
        ("relevance", "Relevance"),
        ("ascending", "Ascending"),
        ("descending", "Descending"),
    ]


def get_classification_choices():
    return [
        ("OFFICIAL", "Official"),
        ("SECRET", "Secret"),
        ("TOP-SECRET", "Top-Secret"),
    ]


def get_where_to_access_choices():
    return [("analytical_platform", "Analytical Platform")]


class SelectWithOptionAttribute(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.domain_model = DomainModel()

    def create_option(
        self, name, urn, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, urn, label, selected, index, subindex, attrs
        )

        if urn:
            option["attrs"]["data-parent"] = self.domain_model.get_parent_urn(urn)

        return option


class SearchForm(forms.Form):
    """Django form to represent data product search page inputs"""

    query = forms.CharField(
        max_length=100,
        strip=False,
        required=False,
        widget=forms.TextInput(attrs={"class": "govuk-input search-input"}),
    )
    domain = forms.ChoiceField(
        choices=get_domain_choices,
        required=False,
        widget=forms.Select(attrs={"form": "searchform", "class": "govuk-select"}),
    )
    subdomain = forms.ChoiceField(
        choices=get_subdomain_choices,
        required=False,
        widget=SelectWithOptionAttribute(
            attrs={"form": "searchform", "class": "govuk-select"}
        ),
    )
    classifications = forms.MultipleChoiceField(
        choices=get_classification_choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "govuk-checkboxes__input", "form": "searchform"}
        ),
    )
    where_to_access = forms.MultipleChoiceField(
        choices=get_where_to_access_choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "govuk-checkboxes__input", "form": "searchform"}
        ),
    )
    sort = forms.ChoiceField(
        choices=get_sort_choices,
        widget=forms.RadioSelect(
            attrs={
                "class": "govuk-radios__input",
                "form": "searchform",
                "onchange": "document.getElementById('searchform').submit();",
            }
        ),
        required=False,
    )
    clear_filter = forms.BooleanField(initial=False, required=False)
    clear_label = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["sort"] = "relevance"

    def encode_without_filter(self, filter_name: str, filter_value: str):
        """Preformat hrefs to drop individual filters"""
        # Deepcopy the cleaned data dict to avoid modifying it inplace
        query_params = deepcopy(self.cleaned_data)
        value = query_params.get(filter_name)
        if isinstance(value, list) and filter_value in value:
            value.remove(filter_value)
        elif isinstance(value, str) and filter_value == value:
            query_params.pop(filter_name)
            if filter_name == "domain":
                query_params.pop("subdomain")
        return f"?{urlencode(query_params, doseq=True)}"
