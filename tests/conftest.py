from random import choice
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.entities import RelationshipType, Table
from data_platform_catalogue.search_types import (
    FacetOption,
    ResultType,
    SearchFacets,
    SearchResponse,
    SearchResult,
)
from datahub.metadata.schema_classes import (
    DataProductAssociationClass,
    DataProductPropertiesClass,
)
from django.test import Client
from faker import Faker

from home.forms.search import SearchForm
from home.service.details import DatabaseDetailsService, DataProductDetailsService
from home.service.glossary import GlossaryService
from home.service.search import SearchService

fake = Faker()


def pytest_addoption(parser):
    parser.addoption("--chromedriver-path", action="store")


@pytest.fixture
def chromedriver_path(request):
    return request.config.getoption("--chromedriver-path")


def generate_search_result(
    result_type: ResultType | None = None, id=None, metadata=None
) -> SearchResult:
    """
    Generate a random search result
    """
    name = fake.name()

    return SearchResult(
        id=id or fake.unique.name(),
        result_type=(
            choice((ResultType.DATA_PRODUCT, ResultType.TABLE))
            if result_type is None
            else result_type
        ),
        name=name,
        fully_qualified_name=name,
        description=fake.paragraph(),
        metadata=metadata or {"search_summary": "a"},
    )


def generate_table_metadata(
    name=None,
    description=None,
    columns_details=None,
    retention_period_in_days=None,
    relations=None,
    domain_name=None,
    tags=None,
    last_modified=None,
    owner=None,
    owner_email=None,
) -> Table:
    """
    Generate a fake table metadata object
    """
    return Table(
        urn="urn:li:table:fake",
        name=name or fake.unique.name(),
        description=description or fake.paragraph(),
        column_details=columns_details or [],
        relationships=relations or {RelationshipType.PARENT: []},
        domain=domain_name,
        tags=tags,
        last_modified=last_modified,
        owner=owner,
        owner_email=owner_email,
    )


def generate_page(page_size=20, result_type: ResultType | None = None):
    """
    Generate a fake search page
    """
    results = []
    for _ in range(page_size):
        results.append(generate_search_result(result_type=result_type))
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
    mock_list_data_product_response(
        mock_catalogue,
        page_results=generate_page(page_size=1, result_type=ResultType.TABLE),
        total_results=1,
    )
    mock_list_database_tables_response(
        mock_catalogue,
        page_results=generate_page(page_size=1, result_type=ResultType.TABLE),
        total_results=1,
    )
    mock_get_table_details_response(mock_catalogue)

    yield mock_catalogue

    patcher.stop()


def mock_list_database_tables_response(mock_catalogue, total_results, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.list_database_tables.return_value = search_response


def mock_get_table_details_response(mock_catalogue):
    mock_catalogue.get_table_details.return_value = Table(
        name="abc",
        description="abc",
        retention_period_in_days=0,
        column_details=[
            {
                "name": "foo",
                "description": "description **with markdown**",
                "type": "string",
            }
        ],
    )


def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.search.return_value = search_response


def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets({"domains": domains})


def mock_list_data_product_response(mock_catalogue, total_results, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.list_data_product_assets.return_value = search_response


def mock_get_dataproduct_aspect(mock_catalogue):
    data_product_association = DataProductAssociationClass(
        destinationUrn="urn:li:dataset:(urn:li:dataPlatform:glue,test.test,PROD)",
        sourceUrn="urn:li:dataProduct:test",
    )

    response = DataProductPropertiesClass(
        name="test", assets=[data_product_association], description="test"
    )
    mock_catalogue.graph.get_aspect.return_value = response


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
            "domain": "urn:li:domain:prison",
            "entity_types": ["TABLE"],
            "where_to_access": ["analytical_platform"],
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
def detail_dataproduct_context(mock_catalogue):
    mock_catalogue.search.return_value = SearchResponse(
        total_results=1,
        page_results=generate_page(page_size=1, result_type=ResultType.DATA_PRODUCT),
    )

    details_service = DataProductDetailsService(urn="urn:li:dataProduct:test")
    context = details_service._get_context()
    return context


@pytest.fixture
def detail_database_context(mock_catalogue):
    mock_catalogue.search.return_value = SearchResponse(
        total_results=1,
        page_results=generate_page(page_size=1, result_type=ResultType.DATABASE),
    )

    details_service = DatabaseDetailsService(urn="urn:li:container:test")
    context = details_service._get_context()
    return context


@pytest.fixture
def dataset_with_parent(mock_catalogue) -> dict[str, Any]:
    """
    Mock the catalogue response for a dataset that is linked to a data product
    """
    data_product = {"urn": "data-product-abc", "name": "parent"}

    table_metadata = generate_table_metadata()
    mock_catalogue.get_table_details.return_value = table_metadata

    mock_catalogue.search.return_value = SearchResponse(
        total_results=1,
        page_results=[
            generate_search_result(
                result_type=ResultType.TABLE,
                id="dataset-abc",
                metadata={"data_products": [data_product]},
            )
        ],
    )

    return {
        "urn": "dataset-abc",
        "parent_entity": data_product,
        "table_metadata": table_metadata,
    }
