from types import GeneratorType
from data_platform_catalogue.search_types import ResultType
from home.service.search import SearchService


class TestSearchService:
    def test_get_context_form(self, valid_form, search_context):
        assert search_context["form"] == valid_form

    def test_get_context_search_result(self, mock_catalogue, search_context):
        assert search_context["results"] == mock_catalogue.search(
        ).page_results
        assert search_context["total_results"] == 100

    def test_get_context_paginator(self, search_context):
        assert search_context["page_obj"].number == 1
        assert isinstance(search_context["page_range"], GeneratorType)
        assert search_context["paginator"].num_pages == 5

    def test_get_context_page_title(self, search_context):
        assert search_context["page_title"] == 'Search for "test" - Data catalogue'

    def test_get_context_label_clear_href(self, search_context):
        assert search_context["label_clear_href"] == {
            "HMCTS": "?query=test&sort=ascending&clear_filter=False&clear_label=False"
        }

    def test_highlight_results_no_query(self, search_service):
        search_service.form.cleaned_data = {"query": ""}
        search_service._highlight_results()
        assert (
            normal.description == highlighted.description
            & normal.metadata == highlighted.metadata
            for normal, highlighted in zip(
                search_service.results.page_results,
                search_service.highlighted_results.page_results,
            )
        )

    def test_highlight_results_with_query(self, search_service):
        search_service.form.cleaned_data = {"query": "a"}
        search_service._highlight_results()

        assert (
            "**a**" in highlighted.description
            & "**" not in normal.description
            for normal, highlighted
            in zip(
                search_service.results.page_results,
                search_service.highlighted_results.page_results,
            )
            if "a" in normal.description
        )
        assert (
            "**a**" in highlighted.metadata["search_summary"]
            & "**" not in normal.metadata["search_summary"]
            for normal, highlighted
            in zip(
                search_service.results.page_results,
                search_service.highlighted_results.page_results,
            )
            if "a" in normal.metadata["search_summary"]
        )


class TestDetailsService:
    def test_get_context(self, detail_context, mock_catalogue):
        assert detail_context["result"] == mock_catalogue.search(
        ).page_results[0]
        result_type = (
            "Data product"
            if mock_catalogue.search().page_results[0].result_type
            == ResultType.DATA_PRODUCT
            else "Table"
        )
        assert detail_context["result_type"] == result_type
        assert (
            detail_context["page_title"]
            == f"{mock_catalogue.search().page_results[0].name} - Data catalogue"
        )
