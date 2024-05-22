from datetime import datetime, timezone
from random import choice
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from data_platform_catalogue.client.datahub_client import DataHubCatalogueClient
from data_platform_catalogue.entities import (
    AccessInformation,
    Column,
    ColumnRef,
    CustomEntityProperties,
    DataSummary,
    DomainRef,
    EntityRef,
    Governance,
    OwnerRef,
    RelationshipType,
    Table,
    TagRef,
    UsageRestrictions,
)
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
from home.service.details import DatabaseDetailsService
from home.service.search import SearchService

fake = Faker()


def pytest_addoption(parser):
    parser.addoption("--chromedriver-path", action="store")
    parser.addoption("--axe-version", action="store")


@pytest.fixture
def chromedriver_path(request):
    return request.config.getoption("--chromedriver-path")


@pytest.fixture
def axe_version(request):
    return request.config.getoption("--axe-version") or "latest"


def generate_search_result(
    result_type: ResultType | None = None, urn=None, metadata=None
) -> SearchResult:
    """
    Generate a random search result
    """
    name = fake.name()

    return SearchResult(
        urn=urn or fake.unique.name(),
        result_type=(
            choice((ResultType.DATABASE, ResultType.TABLE))
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
    relations=None,
) -> Table:
    """
    Generate a fake table metadata object
    """
    return Table(
        urn="urn:li:table:fake",
        display_name="Foo.Dataset",
        name=name or fake.unique.name(),
        fully_qualified_name="Foo.Dataset",
        description=description or fake.paragraph(),
        relationships=relations or {RelationshipType.PARENT: []},
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        column_details=[
            Column(
                name="urn",
                display_name="urn",
                type="string",
                description="The primary identifier for the dataset entity.",
                nullable=False,
                is_primary_key=True,
                foreign_keys=[
                    ColumnRef(
                        name="urn",
                        display_name="urn",
                        table=EntityRef(
                            urn="urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)",
                            display_name="Dataset",
                        ),
                    )
                ],
            ),
        ],
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=CustomEntityProperties(),
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
def mock_catalogue(request):
    if "datahub" in request.keywords:
        yield None
        return

    patcher = patch("home.service.base.GenericService._get_catalogue_client")
    mock_fn = patcher.start()
    mock_catalogue = MagicMock(spec=DataHubCatalogueClient)
    mock_fn.return_value = mock_catalogue
    mock_search_response(
        mock_catalogue, page_results=generate_page(), total_results=100
    )
    mock_search_facets_response(mock_catalogue, domains=generate_options())
    mock_get_glossary_terms_response(mock_catalogue)
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
        urn="urn:li:table:fake",
        display_name="abc",
        name="abc",
        fully_qualified_name="abc",
        description="abc",
        relationships={},
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        column_details=[
            Column(
                name="foo",
                display_name="foo",
                type="string",
                description="description **with markdown**",
                nullable=False,
                is_primary_key=True,
                foreign_keys=[],
            ),
        ],
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
    )


def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.search.return_value = search_response


def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets({"domains": domains})


def mock_get_glossary_terms_response(mock_catalogue):
    mock_catalogue.get_glossary_terms.return_value = SearchResponse(
        total_results=3,
        page_results=[
            SearchResult(
                urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
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
                urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
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
                urn="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
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
                urn="dataset-abc",
                metadata={"data_products": [data_product]},
            )
        ],
    )

    return {
        "urn": "dataset-abc",
        "parent_entity": data_product,
        "table_metadata": table_metadata,
    }
