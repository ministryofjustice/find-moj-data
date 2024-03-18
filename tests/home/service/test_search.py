import re
from types import GeneratorType

import pytest

from home.forms.search import SearchForm
from home.service.search import SearchService, domains_with_their_subdomains


class TestSearchService:
    def test_get_context_form(self, valid_form, search_context):
        assert search_context["form"] == valid_form

    def test_get_context_search_result(self, mock_catalogue, search_context):
        assert search_context["results"] == mock_catalogue.search().page_results
        assert search_context["total_results"] == 100

    def test_get_context_paginator(self, search_context):
        assert search_context["page_obj"].number == 1
        assert isinstance(search_context["page_range"], GeneratorType)
        assert search_context["paginator"].num_pages == 5

    def test_get_context_page_title(self, search_context):
        assert search_context["page_title"] == 'Search for "test" - Data catalogue'

    def test_get_context_label_clear_href(self, search_context):
        assert search_context["label_clear_href"]["domain"] == {
            "HMCTS": (
                "?query=test&"
                "classifications=OFFICIAL&"
                "where_to_access=analytical_platform&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

        assert search_context["label_clear_href"]["availability"] == {
            "analytical_platform": (
                "?query=test&"
                "domain=urn%3Ali%3Adomain%3AHMCTS&"
                "subdomain=&"
                "classifications=OFFICIAL&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

        assert search_context["label_clear_href"]["classifications"] == {
            "OFFICIAL": (
                "?query=test&"
                "domain=urn%3Ali%3Adomain%3AHMCTS&"
                "subdomain=&"
                "where_to_access=analytical_platform&"
                "sort=ascending&"
                "clear_filter=False&"
                "clear_label=False"
            )
        }

    def test__compile_query_word_highlighting_pattern(self, search_service):
        query = "test"
        pattern = search_service._compile_query_word_highlighting_pattern(query)
        assert pattern == re.compile(rf"(\w*{query}\w*)", flags=re.IGNORECASE)

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
        ],
    )
    def test__add_mark_tags(
        self, query, description, marked_description, search_service
    ):
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

        assert (
            search_service.results.page_results
            == search_service.highlighted_results.page_results
        )

    def test_highlight_results_with_query(self, search_service):
        form = SearchForm(data={"query": "a"})
        assert form.is_valid()

        search_service = SearchService(form=form, page="1")

        assert (
            search_service.results.page_results
            != search_service.highlighted_results.page_results
        )


@pytest.mark.parametrize(
    "domain, subdomain, expected_subdomains",
    [
        ("does-not-exist", "", []),
        (
            "urn:li:domain:HMPPS",
            "",
            [
                "urn:li:domain:HMPPS",
                "urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9",
                "urn:li:domain:abe153c1-416b-4abb-be7f-6accf2abb10a",
            ],
        ),
        (
            "urn:li:domain:HMPPS",
            "urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9",
            ["urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9"],
        ),
    ],
)
def test_domain_expansion(domain, subdomain, expected_subdomains):
    assert domains_with_their_subdomains(domain, subdomain) == expected_subdomains
