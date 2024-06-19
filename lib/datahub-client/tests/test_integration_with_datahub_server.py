"""
Integration test that runs against a DataHub server

Run with:
export API_URL='https://catalogue.apps-tools.development.data-platform.service.justice.gov.uk/api'
export JWT_TOKEN=******
poetry run pytest tests/test_integration_with_datahub_server.py
"""

import os
import time
from datetime import datetime, timezone

import pytest
from data_platform_catalogue.client.datahub_client import DataHubCatalogueClient
from data_platform_catalogue.entities import (
    AccessInformation,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Database,
    DataSummary,
    DomainRef,
    EntityRef,
    FurtherInformation,
    Governance,
    OwnerRef,
    RelationshipType,
    Table,
    TagRef,
    UsageRestrictions,
)
from data_platform_catalogue.search_types import MultiSelectFilter, ResultType

jwt_token = os.environ.get("CATALOGUE_TOKEN")
api_url = os.environ.get("CATALOGUE_URL", "")
runs_on_development_server = pytest.mark.skipif("not jwt_token or not api_url")


@runs_on_development_server
def test_search():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    response = client.search()
    assert response.total_results > 20
    assert len(response.page_results) == 20


@runs_on_development_server
def test_search_by_domain():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)

    response = client.search(
        filters=[MultiSelectFilter("domains", ["does-not-exist"])],
        result_types=(ResultType.TABLE,),
    )
    assert response.total_results == 0


@runs_on_development_server
def test_domain_facets_are_returned():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)

    database = Database(
        urn=None,
        name="my_database",
        display_name="database",
        fully_qualified_name="my_database",
        description="little test db",
        governance=Governance(
            data_owner=OwnerRef(
                urn="2e1fa91a-c607-49e4-9be2-6f072ebe27c7",
                display_name="April Gonzalez",
                email="abc@digital.justice.gov.uk",
            ),
            data_stewards=[
                OwnerRef(
                    urn="abc",
                    display_name="Jonjo Shelvey",
                    email="j.shelvey@digital.justice.gov.uk",
                )
            ],
        ),
        domain=DomainRef(urn="LAA", display_name="LAA"),
        database_entities=[
            {
                "entity": {
                    "urn": "urn:li:dataset:fake_table",
                    "properties": {
                        "name": "fake_table",
                        "description": "table description",
                    },
                    "editableProperties": None,
                }
            }
        ],
        last_modified=datetime(2020, 5, 17),
        created=datetime(2020, 5, 17),
        tags=[TagRef(urn="test", display_name="test")],
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=CustomEntityProperties(
            usage_restrictions=UsageRestrictions(
                dpia_required=False,
                dpia_location="",
            ),
            access_information=AccessInformation(
                dc_where_to_access_dataset="analytical_platform",
                s3_location="s3://databucket/",
            ),
        ),
    )
    urn = client.upsert_database(database)

    response = client.search()
    assert response.facets.options("domains")
    assert client.search_facets().options("domains")
    client.graph.hard_delete_entity(urn)


@runs_on_development_server
def test_filter_by_urn():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    client.graph.hard_delete_entity("urn:li:container:my_database")
    database = Database(
        urn=None,
        name="my_database",
        display_name="database",
        fully_qualified_name="my_database",
        description="little test db",
        governance=Governance(
            data_owner=OwnerRef(
                urn="2e1fa91a-c607-49e4-9be2-6f072ebe27c7",
                display_name="April Gonzalez",
                email="abc@digital.justice.gov.uk",
            ),
            data_stewards=[
                OwnerRef(
                    urn="abc",
                    display_name="Jonjo Shelvey",
                    email="j.shelvey@digital.justice.gov.uk",
                )
            ],
        ),
        domain=DomainRef(urn="LAA", display_name="LAA"),
        database_entities=[],
        last_modified=datetime(2020, 5, 17),
        created=datetime(2020, 5, 17),
        tags=[TagRef(urn="test", display_name="test")],
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=CustomEntityProperties(
            usage_restrictions=UsageRestrictions(
                dpia_required=False,
                dpia_location="",
            ),
            access_information=AccessInformation(
                dc_where_to_access_dataset="analytical_platform",
                s3_location="s3://databucket/",
            ),
        ),
    )
    urn = client.upsert_database(database)
    # test search result for urn without entity having display_in_catalogue tag
    response = client.search(
        filters=[MultiSelectFilter(filter_name="urn", included_values=[urn])]
    )
    assert response.total_results == 0

    # add display_in_catalogue tag which will mean urn returned in search result
    database.tags.append(
        TagRef(
            urn="urn:li:tag:display_in_catalogue", display_name="display_in_catalogue"
        )
    )

    urn = client.upsert_database(database)
    time.sleep(2)
    response = client.search(
        filters=[MultiSelectFilter(filter_name="urn", included_values=[urn])]
    )
    assert response.total_results == 1

    client.graph.hard_delete_entity(urn)


@runs_on_development_server
def test_paginated_search_results_unique():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    results1 = client.search(page="1").page_results
    results2 = client.search(page="2").page_results
    assert not any(x in results1 for x in results2)


@runs_on_development_server
def test_list_database_tables():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    assets = client.list_database_tables(urn="urn:li:database:foo", count=20)
    assert assets


@runs_on_development_server
def test_get_glossary_terms_returns():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    assets = client.get_glossary_terms(count=20)
    assert assets


@runs_on_development_server
def test_get_chart():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    table = client.get_chart_details(urn="urn:li:chart:(justice-data,absconds)")
    assert table


@runs_on_development_server
def test_get_dataset():
    client = DataHubCatalogueClient(jwt_token=jwt_token, api_url=api_url)
    table = client.get_table_details(
        urn="urn:li:dataset:(urn:li:dataPlatform:glue,nomis.agency_release_beds,PROD)"
    )
    assert table
