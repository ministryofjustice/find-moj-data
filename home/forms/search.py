from copy import deepcopy
from urllib.parse import urlencode

from data_platform_catalogue.search_types import DomainOption, ResultType
from django import forms
from django.utils.translation import gettext as _

from ..models.domain_model import Domain
from ..service.domain_fetcher import DomainFetcher
from ..service.search_tag_fetcher import SearchTagFetcher


def get_domain_choices() -> list[Domain]:
    """Make Domains API call to obtain domain choices"""
    choices = [
        Domain("", _("All domains")),
    ]
    list_domain_options: list[DomainOption] = DomainFetcher().fetch()
    domains: list[Domain] = [Domain(d.urn, d.name) for d in list_domain_options]
    choices.extend(domains)
    return choices


def get_sort_choices():
    return [
        ("relevance", "Relevance"),
        ("ascending", "Ascending"),
        ("descending", "Descending"),
    ]


def get_where_to_access_choices():
    return [("analytical_platform", _("Analytical Platform"))]


def get_entity_types():
    return sorted(
        [
            (entity.name, entity.name.replace("_", " ").lower().title())
            for entity in ResultType
            if entity.name != "GLOSSARY_TERM"
        ]
    )


def get_tags():
    tags = SearchTagFetcher().fetch()
    return tags


class SearchForm(forms.Form):
    """Django form to represent search page inputs"""

    domain_translate = _("Domain")
    select_filter_translate = _("filter-refresh")

    query = forms.CharField(
        strip=False,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "govuk-input search-input", "type": "search"}
        ),
    )
    domain = forms.ChoiceField(
        choices=get_domain_choices,
        required=False,
        widget=forms.Select(
            attrs={
                "form": "searchform",
                "class": "govuk-select",
                "aria-label": f"{domain_translate} - {select_filter_translate}",
                "onchange": "document.getElementById('searchform').submit();",
            }
        ),
    )
    where_to_access = forms.MultipleChoiceField(
        choices=get_where_to_access_choices,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "govuk-checkboxes__input",
                "form": "searchform",
                "onchange": "document.getElementById('searchform').submit();",
            }
        ),
    )
    entity_types = forms.MultipleChoiceField(
        choices=get_entity_types,
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "govuk-checkboxes__input",
                "form": "searchform",
                "onchange": "document.getElementById('searchform').submit();",
            }
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

    tags = forms.MultipleChoiceField(choices=get_tags, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["sort"] = "relevance"

    def encode_without_filter(self, filter_name: str, filter_value: str):
        """
        Generate a query string that can be used to generate "remove filter"
        links.

        The query string includes all submitted form parameters except
        the one identified by filter_name and filter_value.

        >>> formdata = {'domain': 'urn:li:domain:prison', 'entity_types': ['TABLE']}
        >>> form = SearchForm(formdata)
        >>> assert form.is_valid()

        >>> form.encode_without_filter('domain', 'urn:li:domain:prison')
        '?query=&entity_types=TABLE&sort=&clear_filter=False&clear_label=False'

        >>> form.encode_without_filter('entity_types', 'TABLE')
        '?query=&domain=urn%3Ali%3Adomain%3Aprison&subdomain=&sort=&clear_filter=False&clear_label=False'
        """
        # Deepcopy the cleaned data dict to avoid modifying it inplace
        query_params = deepcopy(self.cleaned_data)
        value = query_params.get(filter_name)
        if isinstance(value, list) and filter_value in value:
            value.remove(filter_value)
        elif isinstance(value, str) and filter_value == value:
            query_params.pop(filter_name)
        return f"?{urlencode(query_params, doseq=True)}"
