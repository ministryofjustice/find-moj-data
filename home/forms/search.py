from copy import deepcopy
from urllib.parse import urlencode

from django import forms


def get_domain_choices():
    """Make API call to obtain domain choices"""
    # TODO: pull in the domains from the catalogue client
    # facets = client.search_facets()
    # domain_list = facets.options("domains")
    return [
        ("urn:li:domain:HMCTS", "HMCTS"),
        ("urn:li:domain:HMPPS", "HMPPS"),
        ("urn:li:domain:OPG", "OPG"),
        ("urn:li:domain:HQ", "HQ"),
    ]


def get_sort_choices():
    return [
        ("relevance", "Relevance"),
        ("ascending", "Ascending"),
        ("descending", "Descending"),
    ]


class SearchForm(forms.Form):
    """Django form to represent data product search page inputs"""

    query = forms.CharField(
        max_length=100,
        strip=False,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "govuk-input search-input"}
        ),
    )
    domains = forms.MultipleChoiceField(
        choices=get_domain_choices,
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

    def encode_without_filter(self, filter_to_remove):
        """Preformat hrefs to drop individual filters"""
        # Deepcopy the cleaned data dict to avoid modifying it inplace
        query_params = deepcopy(self.cleaned_data)

        query_params["domains"].remove(filter_to_remove)
        if len(query_params["domains"]) == 0:
            query_params.pop("domains")

        return f"?{urlencode(query_params, doseq=True)}"
