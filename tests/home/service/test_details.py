from data_platform_catalogue.entities import (
    Chart,
    EntityRef,
    RelationshipType,
    Governance,
    DomainRef,
    OwnerRef,
)
from data_platform_catalogue.search_types import ResultType

from home.service.details import ChartDetailsService, DatasetDetailsService
from tests.conftest import generate_table_metadata


class TestDetailsDatasetService:
    def test_get_context_contains_table_metadata(self, dataset_with_parent):
        service = DatasetDetailsService(dataset_with_parent["urn"])
        context = service.context
        assert context["table"] == dataset_with_parent["table_metadata"]

    def test_get_context_contains_parent(self, mock_catalogue):
        parent = {
            RelationshipType.PARENT: [
                EntityRef(urn="urn:li:container:parent", display_name="parent")
            ],
        }
        mock_table = generate_table_metadata(relations=parent)
        mock_catalogue.get_table_details.return_value = mock_table

        service = DatasetDetailsService("urn:li:datsset:test")
        context = service.context
        assert context["parent_entity"] == EntityRef(
            urn="urn:li:container:parent", display_name="parent"
        )


class TestDatabaseDetailsService:
    def test_get_context_database(self, detail_database_context, mock_catalogue):
        assert (
            detail_database_context["result"] == mock_catalogue.search().page_results[0]
        )
        result_type = (
            "Database"
            if mock_catalogue.search().page_results[0].result_type
            == ResultType.DATABASE
            else "Table"
        )
        assert detail_database_context["result_type"] == result_type
        assert detail_database_context["h1_value"] == "Details"

    def test_get_context_database_tables(self, detail_database_context, mock_catalogue):
        name = mock_catalogue.list_database_tables().page_results[0].name
        mock_table = {
            "name": name,
            "urn": mock_catalogue.list_database_tables().page_results[0].urn,
            "description": mock_catalogue.list_database_tables()
            .page_results[0]
            .description,
            "type": "TABLE",
        }
        assert detail_database_context["tables"][0] == mock_table


class TestDetailsChartService:
    def test_get_context(self, mock_catalogue):
        chart_metadata = Chart(
            name="test",
            description="test",
            external_url="https://www.test.com",
            domain=DomainRef(urn="LAA", display_name="LAA"),
            governance=Governance(
                data_owner=OwnerRef(
                    display_name="", email="Contact email for the user", urn=""
                ),
                data_stewards=[
                    OwnerRef(
                        display_name="", email="Contact email for the user", urn=""
                    )
                ],
            ),
            platform=EntityRef(urn="", display_name="")
        )
        mock_catalogue.get_chart_details.return_value = chart_metadata

        context = ChartDetailsService("urn").context
        expected = {"chart": chart_metadata, "h1_value": "Details"}

        assert context == expected
