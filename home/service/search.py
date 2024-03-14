import re
from copy import deepcopy
from typing import Any

from data_platform_catalogue.search_types import MultiSelectFilter, SortOption
from django.core.paginator import Paginator

from home.forms.domain_model import DomainModel
from home.forms.search import SearchForm

from .base import GenericService


def domains_with_their_subdomains(domain: str, subdomain: str) -> list[str]:
    """
    Users can search by domain, and optionally by subdomain.
    When subdomain is passed, then we can filter on that directly.

    However, when we filter by domain alone, assets tagged to subdomains
    are not automatically included, so we need to include all possible
    subdomains in the filter.
    """
    if subdomain:
        return [subdomain]

    subdomains = DomainModel().subdomains.get(domain, [])
    subdomains = [subdomain[0] for subdomain in subdomains]
    return [domain, *subdomains] if subdomains else []


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        self.domain_model = DomainModel()
        self.form = form
        self.page = page
        self.client = self._get_catalogue_client()
        self.results = self._get_search_results(page, items_per_page)
        self.highlighted_results = self._highlight_results()
        self.paginator = self._get_paginator(items_per_page)
        self.context = self._get_context()

    @staticmethod
    def _build_custom_property_filter(
        filter_param: str, filter_value_list: list[str]
    ) -> list[str]:
        return [f"{filter_param}{filter_value}" for filter_value in filter_value_list]

    def _get_search_results(self, page: str, items_per_page: int):
        if self.form.is_bound:
            form_data = self.form.cleaned_data
        else:
            form_data = {}

        query = form_data.get("query", "")
        sort = form_data.get("sort", "relevance")
        domain = form_data.get("domain", "")
        subdomain = form_data.get("subdomain", "")
        domains_and_subdomains = domains_with_their_subdomains(domain, subdomain)
        classifications = self._build_custom_property_filter(
            "sensitivityLevel=", form_data.get("classifications", [])
        )
        where_to_access = self._build_custom_property_filter(
            "whereToAccessDataset=", form_data.get("where_to_access", [])
        )
        filter_value = []
        if domains_and_subdomains:
            filter_value.append(MultiSelectFilter("domains", domains_and_subdomains))
        if classifications:
            filter_value.append(MultiSelectFilter("customProperties", classifications))
        if where_to_access:
            filter_value.append(MultiSelectFilter("customProperties", where_to_access))

        page_for_search = str(int(page) - 1)
        if sort == "ascending":
            sort_option = SortOption(field="name", ascending=True)
        elif sort == "descending":
            sort_option = SortOption(field="name", ascending=False)
        else:
            sort_option = None

        results = self.client.search(
            query=query,
            page=page_for_search,
            filters=filter_value,
            sort=sort_option,
            count=items_per_page,
        )

        return results

    def _get_paginator(self, items_per_page: int) -> Paginator:
        pages_list = list(range(self.results.total_results))

        return Paginator(pages_list, items_per_page)

    def _generate_label_clear_ref(self) -> dict[str, dict[str, str]] | None:
        if self.form.is_bound:
            domain = self.form.cleaned_data.get("domain", "")
            classifications = self.form.cleaned_data.get("classifications", [])
            where_to_access = self.form.cleaned_data.get("where_to_access", [])
            label_clear_href = {}
            if domain:
                label_clear_href["domain"] = self._generate_domain_clear_href()
            if classifications:
                classifications_clear_href = {}
                for classification in classifications:
                    classifications_clear_href[classification] = (
                        self.form.encode_without_filter(
                            filter_name="classifications", filter_value=classification
                        )
                    )
                label_clear_href["classifications"] = classifications_clear_href

            if where_to_access:
                where_to_access_clear_href = {}
                for access in where_to_access:
                    where_to_access_clear_href[access] = (
                        self.form.encode_without_filter(
                            filter_name="where_to_access", filter_value=access
                        )
                    )
                label_clear_href["availability"] = where_to_access_clear_href
        else:
            label_clear_href = None

        return label_clear_href

    def _generate_domain_clear_href(
        self,
    ) -> dict[str, str]:
        domain = self.form.cleaned_data.get("domain", "")
        subdomain = self.form.cleaned_data.get("subdomain", "")

        label = self.domain_model.get_label(subdomain or domain)

        return {
            label: (
                self.form.encode_without_filter(
                    filter_name="domain", filter_value=domain
                )
            )
        }

    def _get_context(self) -> dict[str, Any]:
        if self.form["query"].value():
            page_title = f'Search for "{self.form["query"].value()}" - Data catalogue'
        else:
            page_title = "Search - Data catalogue"

        context = {
            "form": self.form,
            "results": self.results.page_results,
            "highlighted_results": self.highlighted_results.page_results,
            "page_title": page_title,
            "page_obj": self.paginator.get_page(self.page),
            "page_range": self.paginator.get_elided_page_range(
                self.page, on_each_side=2, on_ends=1
            ),
            "paginator": self.paginator,
            "total_results": self.results.total_results,
            "label_clear_href": self._generate_label_clear_ref(),
            "readable_match_reasons": self._get_match_reason_display_names(),
        }

        return context

    def _highlight_results(self):
        "Take a SearchResponse and add bold markdown where the query appears"
        query = self.form.cleaned_data.get("query") if self.form.is_valid() else ""
        highlighted_results = deepcopy(self.results)

        if query in ("", "*"):
            return highlighted_results

        else:
            pattern = f"({re.escape(query)})"
            for result in highlighted_results.page_results:
                result.description = re.sub(
                    pattern,
                    r"<mark>\1</mark>",
                    result.description,
                    flags=re.IGNORECASE,
                )

            return highlighted_results

    def _get_match_reason_display_names(self):
        return {
            "id": "ID",
            "urn": "URN",
            "domains": "Domain",
            "name": "Name",
            "description": "Description",
            "fieldPaths": "Column name",
            "fieldDescriptions": "Column description",
            "sensitivityLevel": "Sensitivity level",
            "whereToAccessDataset": "Availability",
            "qualifiedName": "Qualified name",
        }
