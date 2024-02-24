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
    return [domain, *subdomains] if subdomains else [domain]


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        self.form = form
        self.page = page
        self.client = self._get_catalogue_client()
        self.results = self._get_search_results(page, items_per_page)
        self.paginator = self._get_paginator(items_per_page)
        self.context = self._get_context()

    def _get_search_results(self, page: str, items_per_page: int):
        if self.form.is_bound:
            form_data = self.form.cleaned_data
        else:
            form_data = {}

        query = form_data.get("query", "")
        sort = form_data.get("sort", "relevance")
        domain = form_data.get("domain", "")
        domains_and_subdomains = domains_with_their_subdomains(domain)
        filter_value = (
            [MultiSelectFilter("domains", domains_and_subdomains)]
            if domains_and_subdomains
            else []
        )

        classifications = form_data.get("classifications", [])
        where_to_access = form_data.get("where_to_access", [])

        custom_properties = {
            "classifications": classifications,
            "where_to_access": where_to_access,
        }

        full_query = self._query_builder(query, custom_properties)
        page_for_search = str(int(page) - 1)
        if sort == "ascending":
            sort_option = SortOption(field="name", ascending=True)
        elif sort == "descending":
            sort_option = SortOption(field="name", ascending=False)
        else:
            sort_option = None

        results = self.client.search(
            query=full_query,
            page=page_for_search,
            filters=filter_value,
            sort=sort_option,
            count=items_per_page,
        )

        return results

    def _get_paginator(self, items_per_page: int) -> Paginator:
        pages_list = list(range(self.results.total_results))

        return Paginator(pages_list, items_per_page)

    def _get_context(self) -> dict[str, Any]:
        if self.form["query"].value():
            page_title = f'Search for "{self.form["query"].value()}" - Data catalogue'
        else:
            page_title = "Search - Data catalogue"

        if self.form.is_bound:
            domain = self.form.cleaned_data.get("domain", "")
            classifications = self.form.cleaned_data.get("classifications", [])
            label_clear_href = {}
            if domain:
                label_clear_href["domain"] = {
                    domain.split(":")[-1]: (self.form.encode_without_filter(domain))
                }
            if classifications:
                classifications_clear_href = {}
                for classification in classifications:
                    classifications_clear_href[
                        classification.split("=")[1]
                    ] = self.form.encode_without_filter(classification)
                label_clear_href["classifications"] = classifications_clear_href
        else:
            label_clear_href = None
        print(f"label clear ref: {label_clear_href}")
        context = {
            "form": self.form,
            "results": self.results.page_results,
            "page_title": page_title,
            "page_obj": self.paginator.get_page(self.page),
            "page_range": self.paginator.get_elided_page_range(
                self.page, on_each_side=2, on_ends=1
            ),
            "paginator": self.paginator,
            "total_results": self.results.total_results,
            "label_clear_href": label_clear_href,
        }

        return context

    @staticmethod
    def _query_builder(query: str, custom_properties: dict[str, list[str]]) -> str:
        """Construct a valid DataHub search query using the input query and the passed
        customProperties.

        Args:
            query (str): User search string
            custom_properties (dict[str, list[str  |  None]]): Dictionary of custom
            property name and custom property values selected to filter on.

        Returns:
            str: advanced query string to pass to DataHub that will include 'filtering'
            logic for custom properties
        """
        # ref: https://datahubproject.io/docs/how/search/#advanced-queries
        custom_property_query: str = "/q customProperties: "
        custom_property_strings: list[str] = []

        for _, value in custom_properties.items():
            if value:
                # within-filter options are inclusive OR
                custom_property_string = " OR ".join(value)
                custom_property_strings.append(custom_property_string)

        if query != "":
            custom_property_strings.append(query)

        # cross-filter options are exclusive AND
        final_query = " AND ".join(custom_property_strings)

        return f"{custom_property_query} {final_query}" if final_query else "*"
