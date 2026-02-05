import os
import re
from urllib.parse import quote

import pytest

from home.forms.search import SearchForm
from home.service.search import SearchService

dev_env = True if os.environ.get("ENV") == "dev" else False


class TestSearchService:
    def test_get_context_form(self, valid_form, search_context):
        assert search_context["form"] == valid_form

    def test_get_context_search_result(self, mock_catalogue, search_context):
        assert search_context["results"] == mock_catalogue.search().page_results
        assert search_context["total_results_str"] == "100"

    def test_get_context_paginator(self, search_context):
        assert search_context["page_obj"].number == 1
        assert search_context["page_obj"].paginator.num_pages == 5

    def test_get_context_h1_value(self, search_context):
        assert search_context["h1_value"] == "Search for data assets"

    def test_get_context_remove_filter_hrefs(self, search_context, valid_subject_area_choice):
        assert search_context["remove_filter_hrefs"]["Subject area"] == {
            valid_subject_area_choice.label: (
                "?query=test&"
                "where_to_access=analytical_platform&"
                "tags=Risk&"
                "entity_types=TABLE&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

        assert search_context["remove_filter_hrefs"]["Where to access"] == {
            "analytical_platform": (
                "?query=test&"
                f"subject_area={quote(valid_subject_area_choice.urn)}&"
                "tags=Risk&"
                "entity_types=TABLE&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

        assert search_context["remove_filter_hrefs"]["Entity types"] == {
            "Table": (
                "?query=test&"
                f"subject_area={quote(valid_subject_area_choice.urn)}&"
                "where_to_access=analytical_platform&"
                "tags=Risk&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

        assert search_context["remove_filter_hrefs"]["Tags"] == {
            "Risk": (
                "?query=test&"
                f"subject_area={quote(valid_subject_area_choice.urn)}&"
                "where_to_access=analytical_platform&"
                "entity_types=TABLE&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

    def test__compile_query_word_highlighting_pattern(self, search_service):
        query = "test"
        pattern = search_service._compile_query_word_highlighting_pattern(query)

        assert pattern == re.compile(rf"((\w*{query}\w*))", flags=re.IGNORECASE)

    @pytest.mark.parametrize(
        "query, description, marked_description",
        [
            (
                "test",
                "This is a test description",
                "This is a <mark>test</mark> description",
            ),
            (
                "OFF",
                "This is a offence description of offences",
                "This is a <mark>offence</mark> description of <mark>offences</mark>",
            ),
            (
                "OFF",
                "offence description of offences",
                "<mark>offence</mark> description of <mark>offences</mark>",
            ),
            (
                "offence description",
                "offence description of offences",
                "<mark>offence description</mark> of <mark>offences</mark>",
            ),
            (
                "offence description",
                "offence abc",
                "<mark>offence</mark> abc",
            ),
            (
                "offence description banana",
                "offence description of offences",
                "<mark>offence</mark> <mark>description</mark> of <mark>offences</mark>",
            ),
        ],
    )
    def test__add_mark_tags(self, query, description, marked_description, search_service):
        pattern = search_service._compile_query_word_highlighting_pattern(query)
        assert (
            search_service._add_mark_tags(
                description,
                pattern,
            )
            == marked_description
        )

    def test_highlight_results_no_query(self):
        form = SearchForm(data={"query": ""})
        assert form.is_valid()

        search_service = SearchService(form=form, page="1")

        assert search_service.results.page_results == search_service.highlighted_results.page_results

    def test_highlight_results_with_query(self, search_service):
        form = SearchForm(data={"query": "a"})
        assert form.is_valid()

        search_service = SearchService(form=form, page="1")

        assert search_service.results.page_results != search_service.highlighted_results.page_results

    # @pytest.mark.parametrize(
    #     "query, formatted_query",
    #     [
    #         ("'abc_def'", "'abc_def'"),
    #         ('"abc_def"', '"abc_def"'),
    #         ("'abc_def_ghi'", "'abc_def_ghi'"),
    #         ('"abc_def_ghi"', '"abc_def_ghi"'),
    #         ("abc_def", "abc def"),
    #         ("abc_def_ghi", "abc def ghi"),
    #     ],
    # )
    # def test_query_format(self, query, formatted_query):
    #     form = SearchForm(data={"query": query})
    #     assert form.is_valid()
    #     search_service = SearchService(form=form, page="1")
    #     assert search_service._format_query_value(query) == formatted_query
