from typing import Any
from copy import deepcopy
from data_platform_catalogue.search_types import MultiSelectFilter, SortOption
from django.core.paginator import Paginator

from home.forms.search import SearchForm

from .base import GenericService


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        self.form = form
        self.page = page
        self.client = self._get_catalogue_client()
        self.results = self._get_search_results(page, items_per_page)
        self.highlighted_results = self._highlight_results()
        self.paginator = self._get_paginator(items_per_page)
        self.context = self._get_context()

    def _get_search_results(self, page: str, items_per_page: int):
        if self.form.is_bound:
            form_data = self.form.cleaned_data
        else:
            form_data = {}
        query = form_data.get("query", "")
        sort = form_data.get("sort", "relevance")
        domains = form_data.get("domains", [])
        filter_value = [MultiSelectFilter(
            "domains", domains)] if domains else []
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

    def _get_context(self) -> dict[str, Any]:
        if self.form["query"].value():
            page_title = f'Search for "{self.form["query"].value()}" - Data catalogue'
        else:
            page_title = "Search - Data catalogue"

        if self.form.is_bound:
            label_clear_href = {
                filter.split(":")[-1]: self.form.encode_without_filter(filter)
                for filter in self.form.cleaned_data.get("domains", [])
            }
        else:
            label_clear_href = None

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
            "readable_match_reasons": self._get_match_reason_display_names(),
        }

        return context

    def _highlight_results(self):
        "Take a SearchResponse and add bold markdown where the query appears"
        string_to_highlight = self.form.cleaned_data.get("query") if self.form.is_valid() else ""
        highlighted_results = deepcopy(self.results)

        if string_to_highlight == "":
            return highlighted_results

        else:
            for result in highlighted_results.page_results:
                metadata = getattr(result, "metadata")
                metadata["search_summary"] = metadata.get("search_summary", "").replace(
                    string_to_highlight, f"**{string_to_highlight}**"
                )
                setattr(result, "metadata", metadata)

                name = getattr(result, "description")
                highlighted_description = name.replace(
                    string_to_highlight, f"**{string_to_highlight}**"
                )
                setattr(result, "description", highlighted_description)

            return highlighted_results

    def _get_match_reason_display_names(self):
        return {
            "urn": "URN",
            "id": "ID",
            "domain": "Domain",
            "name": "Name",
            "description": "Description",
            "fieldPaths": "Column name",
            "fieldDescriptions": "Column description",
        }
