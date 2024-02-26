from random import choice
from unittest.mock import MagicMock, patch

import pytest
from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.search_types import (
    FacetOption,
    ResultType,
    SearchFacets,
    SearchResponse,
    SearchResult,
)
from django.test import Client
from faker import Faker

from home.forms.search import SearchForm
from home.service.details import DetailsService
from home.service.search import SearchService
from home.service.glossary import GlossaryService

fake = Faker()


def generate_page(page_size=20):
    """
    Generate a fake search page
    """
    results = []
    for _ in range(page_size):
        results.append(
            SearchResult(
                id=fake.unique.name(),
                result_type=choice(
                    (ResultType.DATA_PRODUCT, ResultType.TABLE)),
                name=fake.name(),
                description=fake.paragraphs(),
            )
        )
    return results


def generate_options(num_options=5):
    """
    Generate a list of options for the search facets
    """
    results = []
    for _ in range(num_options):
        results.append(
            FacetOption(
                value=fake.name(),
                label=fake.name(),
                count=fake.random_int(min=0, max=100),
            )
        )
    return results


@pytest.fixture(autouse=True)
def client():
    client = Client()
    return client


@pytest.fixture(autouse=True)
def mock_catalogue():
    patcher = patch("home.service.base.GenericService._get_catalogue_client")
    mock_fn = patcher.start()
    mock_catalogue = MagicMock(spec=BaseCatalogueClient)
    mock_fn.return_value = mock_catalogue
    mock_search_response(
        mock_catalogue, page_results=generate_page(), total_results=100
    )
    mock_search_facets_response(mock_catalogue, domains=generate_options())
    mock_get_glossary_terms_response(mock_catalogue)

    yield mock_catalogue

    patcher.stop()


def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.search.return_value = search_response


def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets(
        {"domains": domains})

def mock_get_glossary_terms_response(mock_catalogue):
    mock_catalogue.get_glossary_terms.return_value = SearchResponse(
        total_results=3,
        page_results=[
            SearchResult(
                id="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                name="IAO",
                description="Information asset owner.\n",
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
                result_type="GLOSSARY_TERM",
            ),
            SearchResult(
                id="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                name="Other term",
                description="Term description to test groupings work",
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
                result_type="GLOSSARY_TERM",
            ),
            SearchResult(
                id="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                name="Security classification",
                description="Only data that is 'official'",
                metadata={"parentNodes": []},
                result_type="GLOSSARY_TERM",
            ),
        ],
    )

@pytest.fixture
def valid_form():
    valid_form = SearchForm(
        data={
            "query": "test",
            "domains": ["urn:li:domain:HMCTS"],
            "sort": "ascending",
            "clear_filter": False,
            "clear_label": False,
        }
    )
    assert valid_form.is_valid()

    return valid_form


@pytest.fixture
def search_context(valid_form):
    search_service = SearchService(form=valid_form, page="1")
    context = search_service._get_context()
    return context


@pytest.fixture
def detail_context(mock_catalogue):
    mock_catalogue.search.return_value = SearchResponse(
        total_results=1, page_results=generate_page(page_size=1)
    )
    details_service = DetailsService(urn="urn:li:dataProduct:test")
    context = details_service._get_context()
    return context

# @pytest.fixture
# def glossary_context(mock_catalogue):
#     mock_catalogue.search.return_value = SearchResponse(
#         total_results=1, page_results=generate_page(page_size=1)
#     )
#     glossary_service = GlossaryService()
#     return glossary_service.context
