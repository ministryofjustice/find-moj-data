from types import GeneratorType
from unittest.mock import patch

import pytest
from data_platform_catalogue.search_types import (
    ResultType,
    SearchResponse,
    SearchResult,
)

from home.service.glossary import GlossaryService
from home.service.search import SearchForm, SearchService, domains_with_their_subdomains


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

    def test_highlight_results_no_query(self, search_service):
        search_service.form.cleaned_data = {"query": ""}
        search_service._highlight_results()
        assert (
            normal.description == highlighted.description
            and normal.metadata == highlighted.metadata
            for normal, highlighted in zip(
                search_service.results.page_results,
                search_service.highlighted_results.page_results,
            )
        )

    def test_highlight_results_with_case_insensitive_query(self):
        # The descriptions are all in lower case, so search upper case
        # to test case insensitivity
        form = SearchForm(data={"query": "A"})
        assert form.is_valid()
        service = SearchService(form=form, page="1")

        descriptions = [result.description for result in service.results.page_results]
        highlighted_descriptions = [
            result.description for result in service.highlighted_results.page_results
        ]

        assert descriptions != highlighted_descriptions
        assert (
            "**a**" or "**A**" in highlighted.description
            for normal, highlighted in zip(
                service.results.page_results,
                service.highlighted_results.page_results,
            )
            if "a" or "A" in normal.description
        )


class TestDetailsDataProductService:
    def test_get_context_data_product(self, detail_dataproduct_context, mock_catalogue):
        assert (
            detail_dataproduct_context["result"]
            == mock_catalogue.search().page_results[0]
        )
        result_type = (
            "Data product"
            if mock_catalogue.search().page_results[0].result_type
            == ResultType.DATA_PRODUCT
            else "Table"
        )
        assert detail_dataproduct_context["result_type"] == result_type
        assert (
            detail_dataproduct_context["page_title"]
            == f"{mock_catalogue.search().page_results[0].name} - Data catalogue"
        )

    def test_get_context_data_product_tables(
        self, detail_dataproduct_context, mock_catalogue
    ):
        name = mock_catalogue.list_data_product_assets().page_results[0].name
        mock_table = {
            "name": name,
            "urn": mock_catalogue.list_data_product_assets().page_results[0].id,
            "description": mock_catalogue.list_data_product_assets()
            .page_results[0]
            .description,
            "type": "TABLE",
        }
        assert detail_dataproduct_context["tables"][0] == mock_table


class TestGlossaryService:
    def test_get_context(self):
        glossary_context = GlossaryService()
        expected_context = {
            "results": [
                {
                    "name": "Data protection terms",
                    "members": [
                        SearchResult(
                            id="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                            result_type="GLOSSARY_TERM",
                            name="IAO",
                            description="Information asset owner.\n",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data protection terms",
                                            "description": "Data protection terms",
                                        }
                                    }
                                ]
                            },
                            tags=[],
                            last_updated=None,
                        ),
                        SearchResult(
                            id="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                            result_type="GLOSSARY_TERM",
                            name="Other term",
                            description="Term description to test groupings work",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data protection terms",
                                            "description": "Data protection terms",
                                        }
                                    }
                                ]
                            },
                            tags=[],
                            last_updated=None,
                        ),
                    ],
                    "description": "Data protection terms",
                },
                {
                    "name": "Unsorted",
                    "members": [
                        SearchResult(
                            id="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                            result_type="GLOSSARY_TERM",
                            name="Security classification",
                            description="Only data that is 'official'",
                            matches={},
                            metadata={"parentNodes": []},
                            tags=[],
                            last_updated=None,
                        )
                    ],
                    "description": "",
                },
            ]
        }

        assert expected_context == glossary_context.context


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
