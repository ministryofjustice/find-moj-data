from copy import deepcopy
from urllib.parse import urlencode

from data_platform_catalogue.search_types import ListDomainOption, ResultType
from django import forms

from ..models.domain_model import Domain, DomainModel
from ..service.list_domain_fetcher import ListDomainFetcher
from ..service.search_facet_fetcher import SearchFacetFetcher
from ..service.search_tag_fetcher import SearchTagFetcher


def get_domain_choices() -> list[Domain]:
    """Make API call to obtain domain choices"""
    choices = [
        Domain("", "All domains"),
    ]
    facets = SearchFacetFetcher().fetch()
    choices.extend(DomainModel(facets).top_level_domains)
    return choices


def get_list_domain_choices() -> list[Domain]:
    """Make ListDomains API call to obtain domain choices"""
    choices = [
        Domain("", "All domains"),
    ]
    list_domain_options: list[ListDomainOption] = ListDomainFetcher().fetch()
    domains: list[Domain] = [Domain(d.urn, d.name) for d in list_domain_options]
    choices.extend(domains)
    return choices


def get_subdomain_choices() -> list[Domain]:
    choices = [Domain("", "All subdomains")]
    facets = SearchFacetFetcher().fetch()
    choices.extend(DomainModel(facets).all_subdomains())
    return choices


def get_sort_choices():
    return [
        ("relevance", "Relevance"),
        ("ascending", "Ascending"),
        ("descending", "Descending"),
    ]


def get_where_to_access_choices():
    return [("analytical_platform", "Analytical Platform")]


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


class SelectWithOptionAttribute(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_model = None

    def create_option(
        self, name, urn, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, urn, label, selected, index, subindex, attrs
        )

        facets = SearchFacetFetcher().fetch()
        self.domain_model = self.domain_model or DomainModel(facets)

        if urn:
            option["attrs"]["data-parent"] = self.domain_model.get_parent_urn(urn)

        return option


class SearchForm(forms.Form):
    """Django form to represent search page inputs"""

    query = forms.CharField(
        max_length=100,
        strip=False,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "govuk-input search-input", "type": "search"}
        ),
    )
    domain = forms.ChoiceField(
        choices=get_list_domain_choices,
        required=False,
        widget=forms.Select(
            attrs={
                "form": "searchform",
                "class": "govuk-select",
                "aria-label": "Domain",
                "onchange": "document.getElementById('searchform').submit();",
            }
        ),
    )
    subdomain = forms.ChoiceField(
        choices=get_subdomain_choices,
        required=False,
        widget=SelectWithOptionAttribute(
            attrs={"form": "searchform", "class": "govuk-select"}
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
            if filter_name == "domain":
                query_params.pop("subdomain")
        return f"?{urlencode(query_params, doseq=True)}"
