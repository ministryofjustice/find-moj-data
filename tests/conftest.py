from random import choice
from unittest.mock import MagicMock, patch

import pytest
from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.search_types import (FacetOption, ResultType,
                                                  SearchFacets, SearchResponse,
                                                  SearchResult)
from django.test import Client
from faker import Faker

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
    mock_search_response(mock_catalogue, page_results=generate_page(), total_results=100)
    mock_search_facets_response(mock_catalogue, domains=generate_options())

    yield mock_catalogue

    patcher.stop()

def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(total_results=total_results, page_results=page_results)
    mock_catalogue.search.return_value = search_response

def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets({"domains": domains})
