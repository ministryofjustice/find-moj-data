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

fake = Faker()


def pytest_addoption(parser):
    parser.addoption("--chromedriver-path", action="store")


@pytest.fixture
def chromedriver_path(request):
    return request.config.getoption("--chromedriver-path")


def generate_page(page_size=20):
    """
    Generate a fake search page
    """
    results = []
    for _ in range(page_size):
        results.append(
            SearchResult(
                id=fake.unique.name(),
                result_type=choice((ResultType.DATA_PRODUCT, ResultType.TABLE)),
                name=fake.name(),
                description=fake.paragraph(),
                metadata={"search_summary": "a"},
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

    yield mock_catalogue

    patcher.stop()


def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.search.return_value = search_response


def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets({"domains": domains})


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
def search_service(valid_form):
    return SearchService(form=valid_form, page="1")


@pytest.fixture
def search_context(search_service):
    return search_service.context


@pytest.fixture
def detail_context(mock_catalogue):
    mock_catalogue.search.return_value = SearchResponse(
        total_results=1, page_results=generate_page(page_size=1)
    )
    details_service = DetailsService(urn="urn:li:dataProduct:test")
    context = details_service._get_context()
    return context
