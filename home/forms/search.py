from copy import deepcopy
from urllib.parse import urlencode

from django import forms


def get_domain_choices() -> list[tuple[str, str]]:
    """Make API call to obtain domain choices"""
    # TODO: pull in the domains from the catalogue client
    # facets = client.search_facets()
    # domain_list = facets.options("domains")
    return [
        ("", "All Domains"),
        ("urn:li:domain:HMCTS", "HMCTS"),
        ("urn:li:domain:HMPPS", "HMPPS"),
        ("urn:li:domain:HQ", "HQ"),
        ("urn:li:domain:LAA", "LAA"),
        ("urn:li:domain:OPG", "OPG"),
    ]


def get_subdomain_choices(domain):
    # TODO: pull in the subdomains from the catalogue client so we don't need to hardcode
    return {
        "urn:li:domain:HMPPS": [
            ("urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9", "Prisons"),
            ("urn:li:domain:abe153c1-416b-4abb-be7f-6accf2abb10a", "Probation"),
        ],
        "urn:li:domain:HMCTS": [
            ("urn:li:domain:4d77af6d-9eca-4c44-b189-5f1addffae55", "Civil courts"),
            ("urn:li:domain:31754f66-33df-4a73-b039-532518bc765e", "Crown courts"),
            ("urn:li:domain:81adfe94-1284-46a2-9179-945ad2a76c14", "Family courts"),
            (
                "urn:li:domain:b261176c-d8eb-4111-8454-c0a1fa95005f",
                "Magistrates courts",
            ),
        ],
        "urn:li:domain:OPG": [
            (
                "urn:li:domain:bc091f6c-7674-4c82-a315-f5489398f099",
                "Lasting power of attourney",
            ),
            (
                "urn:li:domain:efb9ade3-3c5d-4c5c-b451-df9f2d8136f5",
                "Supervision orders",
            ),
        ],
        "urn:li:domain:HQ": [
            ("urn:li:domain:9fb7ff13-6c7e-47ef-bef1-b13b23fd8c7a", "Estates"),
            ("urn:li:domain:e4476e66-37a1-40fd-83b9-c908f805d8f4", "Finance"),
            ("urn:li:domain:0985731b-8e1c-4b4a-bfc0-38e58d8ba8a1", "People"),
            ("urn:li:domain:a320c915-0b43-4277-9769-66615aab4adc", "Performance"),
        ],
        "urn:li:domain:LAA": [
            (
                "urn:li:domain:24344488-d770-437a-ba6f-e6129203b927",
                "Civil legal advice",
            ),
            ("urn:li:domain:Legal%20Aid", "Legal aid"),
            ("urn:li:domain:5c423c06-d328-431f-8634-7a7e86928819", "Public defender"),
        ],
    }.get(domain, [])


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
        widget=forms.Select(
            attrs={
                "form": "searchform",
                "class": "govuk-select",
                "aria-label": "domain",
            }
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
        return f"?{urlencode(query_params, doseq=True)}"
