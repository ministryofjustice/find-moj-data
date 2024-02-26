from types import GeneratorType

import pytest
from data_platform_catalogue.search_types import (
    ResultType,
    SearchResponse,
    SearchResult,
)
from unittest.mock import patch
from home.service.search import domains_with_their_subdomains
from home.service.glossary import GlossaryService


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
        assert search_context["label_clear_href"] == {
            "HMCTS": "?query=test&sort=ascending&clear_filter=False&clear_label=False"
        }


class TestDetailsService:
    def test_get_context(self, detail_context, mock_catalogue):
        assert detail_context["result"] == mock_catalogue.search().page_results[0]
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
    "domain, expected_subdomains",
    [
        ("does-not-exist", ["does-not-exist"]),
        (
            "urn:li:domain:HMPPS",
            [
                "urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9",
                "urn:li:domain:abe153c1-416b-4abb-be7f-6accf2abb10a",
                "urn:li:domain:HMPPS",
            ],
        ),
    ],
)
def test_domain_expansion(domain, expected_subdomains):
    assert domains_with_their_subdomains([domain]) == expected_subdomains
