import re
from copy import deepcopy
from typing import Any

from data_platform_catalogue.search_types import MultiSelectFilter, SortOption
from django.core.paginator import Paginator

from home.forms.search import SearchForm, get_subdomain_choices

from .base import GenericService


def domains_with_their_subdomains(domain: str) -> list[str]:
    """
    When assets are tagged to subdomains, they are not included in search results if
    we filter by domain alone. We need to include all possible subdomains in the filter.
    """
    subdomains = get_subdomain_choices(domain)
    subdomains = [subdomain[0] for subdomain in subdomains]
    return [domain, *subdomains] if subdomains else []


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        self.form = form
        self.page = page
        self.client = self._get_catalogue_client()
        self.results = self._get_search_results(page, items_per_page)
        self.highlighted_results = self._highlight_results()
        self.paginator = self._get_paginator(items_per_page)
        self.context = self._get_context()

    @staticmethod
    def _build_filter_strings(
        filter_param: str, filter_value_list: list[str]
    ) -> list[str]:
        return (
            [f"{filter_param}{filter_value}" for filter_value in filter_value_list]
            if filter_value_list
            else []
        )

    def _get_search_results(self, page: str, items_per_page: int):
        if self.form.is_bound:
            form_data = self.form.cleaned_data
        else:
            form_data = {}

        query = form_data.get("query", "")
        sort = form_data.get("sort", "relevance")
        domain = form_data.get("domain", "")
        domains_and_subdomains = domains_with_their_subdomains(domain)
        classifications = self._build_filter_strings(
            "sensitivityLevel=", form_data.get("classifications", [])
        )
        where_to_access = self._build_filter_strings(
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

    def _generate_label_clear_ref(self) -> dict[str, dict[str, str]]:
        if self.form.is_bound:
            domain = self.form.cleaned_data.get("domain", "")
            classifications = self.form.cleaned_data.get("classifications", [])
            where_to_access = self.form.cleaned_data.get("where_to_access", [])
            label_clear_href = {}
            if domain:
                label_clear_href["domain"] = {
                    domain.split(":")[-1]: (
                        self.form.encode_without_filter(
                            filter_name="domain", filter_value=domain
                        )
                    )
                }
            if classifications:
                classifications_clear_href = {}
                for classification in classifications:
                    classifications_clear_href[
                        classification
                    ] = self.form.encode_without_filter(
                        filter_name="classifications", filter_value=classification
                    )
                label_clear_href["classifications"] = classifications_clear_href

            if where_to_access:
                where_to_access_clear_href = {}
                for access in where_to_access:
                    where_to_access_clear_href[
                        access
                    ] = self.form.encode_without_filter(
                        filter_name="where_to_access", filter_value=access
                    )
                label_clear_href["availability"] = where_to_access_clear_href
        else:
            label_clear_href = None
        return label_clear_href

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
                    r"**\1**",
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
        }
