import re
from copy import deepcopy
from typing import Any

from django.conf import settings
from django.core.paginator import Paginator
from nltk.stem import PorterStemmer

from datahub_client.entities import FindMoJdataEntityMapper, Mappers
from datahub_client.search.search_types import (
    MultiSelectFilter,
    SearchResponse,
    SortOption,
    SubjectAreaOption,
)
from home.forms.search import SearchForm

from .base import GenericService
from .subject_area_fetcher import SubjectAreaFetcher


class SearchService(GenericService):
    def __init__(self, form: SearchForm, page: str, items_per_page: int = 20):
        subject_areas: list[SubjectAreaOption] = SubjectAreaFetcher().fetch()

        self.subject_area_labels = {}
        for subject_area in subject_areas:
            self.subject_area_labels[subject_area.urn] = subject_area.name

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

    @staticmethod
    def _build_entity_types(
        entity_types: list[str],
    ) -> tuple[FindMoJdataEntityMapper, ...]:
        default_entities = tuple(
            Mapper for Mapper in Mappers if Mapper.datahub_type.value != "GLOSSARY_TERM"
        )
        chosen_entities = tuple(
            Mapper
            for Mapper in Mappers
            if Mapper.find_moj_data_type.name in entity_types
        )

        return chosen_entities if chosen_entities else default_entities

    @staticmethod
    def _format_query_value(query: str) -> str:
        query_pattern: str = r"^[\"'].+[\"']$"
        # Datahub treats any query with underscores as exact, so if the string is not quoted,
        # we convert underscores to spaces so that we get partial matches as well.
        if not re.match(query_pattern, query):
            query = query.replace("_", " ")
        return query

    def _get_search_results(self, page: str, items_per_page: int) -> SearchResponse:
        form_data = self.form_data
        query = self._format_query_value(form_data.get("query", ""))

        # we want to sort results ascending when a user is browsing data via
        # non-keyword searches - otherwise we use the default relevant ordering
        sort = (
            form_data.get("sort", "relevance")
            if query not in ["*", ""]
            else "ascending"
        )

        subject_area = form_data.get("subject_area", "")
        tags = form_data.get("tags", "")
        where_to_access = self._build_custom_property_filter(
            "dc_where_to_access_dataset=", form_data.get("where_to_access", [])
        )
        entity_types = self._build_entity_types(form_data.get("entity_types", []))

        filter_value = []
        if subject_area:
            filter_value.append(MultiSelectFilter("tags", [subject_area]))
        if where_to_access:
            filter_value.append(MultiSelectFilter("customProperties", where_to_access))
        if tags:
            filter_value.append(
                MultiSelectFilter("tags", [f"urn:li:tag:{tag}" for tag in tags])
            )

        page_for_search = str(int(page) - 1)
        if sort == "ascending":
            sort_option = SortOption(field="_entityName", ascending=True)
        elif sort == "descending":
            sort_option = SortOption(field="_entityName", ascending=False)
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
            subject_area = self.form.cleaned_data.get("subject_area", "")
            entity_types = self.form.cleaned_data.get("entity_types", [])
            where_to_access = self.form.cleaned_data.get("where_to_access", [])
            tags = self.form.cleaned_data.get("tags", [])
            remove_filter_hrefs = {}
            if subject_area:
                remove_filter_hrefs["Subject area"] = (
                    self._generate_subject_area_clear_href()
                )
            if entity_types:
                entity_types_clear_href = {}
                for entity_type in entity_types:
                    entity_types_clear_href[entity_type.lower().title()] = (
                        self.form.encode_without_filter(
                            filter_name="entity_types", filter_value=entity_type
                        )
                    )
                remove_filter_hrefs["Entity types"] = entity_types_clear_href

            if where_to_access:
                where_to_access_clear_href = {}
                for access in where_to_access:
                    where_to_access_clear_href[access] = (
                        self.form.encode_without_filter(
                            filter_name="where_to_access", filter_value=access
                        )
                    )
                remove_filter_hrefs["Where to access"] = where_to_access_clear_href

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

    def _generate_subject_area_clear_href(
        self,
    ) -> dict[str, str]:
        subject_area = self.form.cleaned_data.get("subject_area", "")

        label = self.subject_area_labels.get(subject_area, subject_area)

        return {
            label: (
                self.form.encode_without_filter(
                    filter_name="subject_area", filter_value=subject_area
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
            "malformed_result_urns": self.results.malformed_result_urns,
            "highlighted_results": self.highlighted_results.page_results,
            "h1_value": "Search MoJ data",
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

    def _highlight_results(self) -> SearchResponse:
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

    @staticmethod
    def _get_match_reason_display_names():
        return {
            "id": "ID",
            "urn": "URN",
            "title": "Title",
            "name": "Name",
            "description": "Description",
            "fieldPaths": "Column name",
            "fieldDescriptions": "Column description",
            "dc_where_to_access_dataset": "Available on",
            "qualifiedName": "Qualified name",
        }
