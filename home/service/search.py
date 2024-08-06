import re
from copy import deepcopy
from typing import Any

from data_platform_catalogue.search_types import (
    DomainOption,
    MultiSelectFilter,
    ResultType,
    SearchResponse,
    SortOption,
)
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from nltk.stem import PorterStemmer

from home.forms.search import SearchForm
from home.models.domain_model import DomainModel

from .base import GenericService
from .domain_fetcher import DomainFetcher


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        domains: list[DomainOption] = DomainFetcher().fetch()
        self.domain_model = DomainModel(domains)
        self.stemmer = PorterStemmer()
        self.form = form
        if self.form.is_bound:
            self.form_data = self.form.cleaned_data
        else:
            self.form_data = {}
        self.page = page
        self.client = self._get_catalogue_client()
        self.results = self._get_search_results(page, items_per_page)
        self.highlighted_results = self._highlight_results()
        self.paginator = self._get_paginator(items_per_page)
        self.context = self._get_context(items_per_page)

    @staticmethod
    def _build_custom_property_filter(
        filter_param: str, filter_value_list: list[str]
    ) -> list[str]:
        return [f"{filter_param}{filter_value}" for filter_value in filter_value_list]

    def _build_entity_types(self, entity_types: list[str]) -> tuple[ResultType, ...]:
        default_entities = tuple(
            entity for entity in ResultType if entity.name != "GLOSSARY_TERM"
        )
        chosen_entities = (
            tuple(ResultType[entity] for entity in entity_types)
            if entity_types
            else None
        )
        return chosen_entities if chosen_entities else default_entities

    def _get_search_results(self, page: str, items_per_page: int) -> SearchResponse:
        form_data = self.form_data

        # Workaround for https://github.com/datahub-project/datahub/issues/10505
        query = form_data.get("query", "").replace("_", " ")
        sort = form_data.get("sort", "relevance")
        domain = form_data.get("domain", "")
        tags = form_data.get("tags", "")
        where_to_access = self._build_custom_property_filter(
            "dc_where_to_access_dataset=", form_data.get("where_to_access", [])
        )
        entity_types = self._build_entity_types(form_data.get("entity_types", []))
        filter_value = []
        if domain:
            filter_value.append(MultiSelectFilter("domains", [domain]))
        if where_to_access:
            filter_value.append(MultiSelectFilter("customProperties", where_to_access))
        if tags:
            filter_value.append(
                MultiSelectFilter("tags", [f"urn:li:tag:{tag}" for tag in tags])
            )

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
            result_types=entity_types,
            sort=sort_option,
            count=items_per_page,
        )

        return results

    def _get_paginator(self, items_per_page: int) -> Paginator:
        pages_list = list(range(self.results.total_results))

        return Paginator(pages_list, items_per_page)

    def _generate_remove_filter_hrefs(self) -> dict[str, dict[str, str]] | None:
        if self.form.is_bound:
            domain = self.form.cleaned_data.get("domain", "")
            entity_types = self.form.cleaned_data.get("entity_types", [])
            where_to_access = self.form.cleaned_data.get("where_to_access", [])
            tags = self.form.cleaned_data.get("tags", [])
            remove_filter_hrefs = {}
            if domain:
                remove_filter_hrefs["domain"] = self._generate_domain_clear_href()
            if entity_types:
                entity_types_clear_href = {}
                for entity_type in entity_types:
                    entity_types_clear_href[entity_type.lower().title()] = (
                        self.form.encode_without_filter(
                            filter_name="entity_types", filter_value=entity_type
                        )
                    )
                remove_filter_hrefs["Entity Types"] = entity_types_clear_href

            if where_to_access:
                where_to_access_clear_href = {}
                for access in where_to_access:
                    where_to_access_clear_href[access] = (
                        self.form.encode_without_filter(
                            filter_name="where_to_access", filter_value=access
                        )
                    )
                remove_filter_hrefs["Where To Access"] = where_to_access_clear_href

            if tags:
                tags_clear_href = {}
                for tag in tags:
                    tags_clear_href[tag] = self.form.encode_without_filter(
                        filter_name="tags", filter_value=tag
                    )
                remove_filter_hrefs["Tags"] = tags_clear_href
        else:
            remove_filter_hrefs = None

        return remove_filter_hrefs

    def _generate_domain_clear_href(
        self,
    ) -> dict[str, str]:
        domain = self.form.cleaned_data.get("domain", "")

        label = self.domain_model.get_label(domain)

        return {
            label: (
                self.form.encode_without_filter(
                    filter_name="domain", filter_value=domain
                )
            )
        }

    def _get_context(self, items_per_page: int) -> dict[str, Any]:
        if self.results.total_results >= settings.MAX_RESULTS:
            total_results = f"{settings.MAX_RESULTS}+"
        else:
            total_results = str(self.results.total_results)

        context = {
            "form": self.form,
            "results": self.results.page_results,
            "highlighted_results": self.highlighted_results.page_results,
            "h1_value": _("Search"),
            "page_obj": self.paginator.get_page(self.page),
            "page_range": self.paginator.get_elided_page_range(  # type: ignore
                self.page, on_each_side=2, on_ends=1
            ),
            "number_of_words": len(self.form_data.get("query", "").split()),
            "paginator": self.paginator,
            "results_per_page": items_per_page,
            "total_results_str": total_results,
            "total_results": self.results.total_results,
            "remove_filter_hrefs": self._generate_remove_filter_hrefs(),
            "readable_match_reasons": self._get_match_reason_display_names(),
        }

        return context

    def _highlight_results(self):
        "Take a SearchResponse and add bold markdown where the query appears"
        query = self.form.cleaned_data.get("query", "") if self.form.is_valid() else ""
        highlighted_results = deepcopy(self.results)

        if query in ("", "*"):
            return highlighted_results

        else:
            query_word_highlighting_pattern = (
                self._compile_query_word_highlighting_pattern(query)
            )
            for result in highlighted_results.page_results:
                result.description = self._add_mark_tags(
                    result.description or "", query_word_highlighting_pattern
                )
            return highlighted_results

    def _compile_query_word_highlighting_pattern(self, query: str) -> re.Pattern:
        terms = [self.stemmer.stem(term) for term in query.split()]
        if len(terms) > 1:
            terms = [query] + terms

        pattern = "|".join([r"(\w*{}\w*)".format(re.escape(word)) for word in terms])

        return re.compile(rf"({pattern})", flags=re.IGNORECASE)

    @staticmethod
    def _add_mark_tags(description: str, pattern: re.Pattern) -> str:
        return pattern.sub(r"<mark>\1</mark>", description)

    def _get_match_reason_display_names(self):
        return {
            "id": "ID",
            "urn": "URN",
            "domains": "Domain",
            "title": "Title",
            "name": "Name",
            "description": "Description",
            "fieldPaths": "Column name",
            "fieldDescriptions": "Column description",
            "sensitivityLevel": "Sensitivity level",
            "dc_where_to_access_dataset": "Available on",
            "qualifiedName": "Qualified name",
        }
