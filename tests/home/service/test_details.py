from data_platform_catalogue.entities import (
    Chart,
    CustomEntityProperties,
    DomainRef,
    EntityRef,
    FurtherInformation,
    Governance,
    OwnerRef,
    RelationshipType,
)

from home.service.details import (
    ChartDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
)
from tests.conftest import generate_database_metadata, generate_table_metadata


class TestDatasetDetailsService:
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

    def test_get_context_contains_slack(self, mock_catalogue):
        custom_properties = CustomEntityProperties(
            further_information=FurtherInformation(
                dc_slack_channel_name="test",
                dc_slack_channel_url="https://test_url.com",
            )
        )
        mock_table = generate_table_metadata(custom_properties=custom_properties)
        mock_catalogue.get_table_details.return_value = mock_table

        service = DatasetDetailsService("urn:li:datsset:test")
        context = service.context
        assert context["table"].custom_properties == custom_properties
        assert (
            context["table"].custom_properties.further_information.dc_slack_channel_name
            == "test"
        )


class TestDatabaseDetailsService:
    def test_get_context_database(self, mock_catalogue):
        mock_database_name = "urn:li:container:fake"
        mock_database_metadata = generate_database_metadata(name=mock_database_name)
        mock_catalogue.get_database_details.return_value = mock_database_metadata

        service = DatabaseDetailsService(mock_database_name)
        context = service.context
        assert context["database"] == mock_database_metadata

    def test_get_context_contains_slack(self, mock_catalogue):
        custom_properties = CustomEntityProperties(
            further_information=FurtherInformation(
                dc_slack_channel_name="test",
                dc_slack_channel_url="https://test_url.com",
            )
        )
        mock_database_name = "urn:li:container:fake"
        mock_database_metadata = generate_database_metadata(
            name=mock_database_name, custom_properties=custom_properties
        )
        mock_catalogue.get_database_details.return_value = mock_database_metadata

        service = DatabaseDetailsService(mock_database_name)
        context = service.context

        assert context["database"].custom_properties == custom_properties
        assert (
            context[
                "database"
            ].custom_properties.further_information.dc_slack_channel_name
            == "test"
        )

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


class TestChartDetailsService:
    def test_get_context(self, mock_catalogue):
        chart_metadata = Chart(
            urn="urn:li:chart:(justice-data,test)",
            name="test",
            display_name="test",
            fully_qualified_name="test",
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
            platform=EntityRef(urn="", display_name=""),
        )
        mock_catalogue.get_chart_details.return_value = chart_metadata

        context = ChartDetailsService("urn").context
        expected = {"chart": chart_metadata, "h1_value": "Details"}

        assert context == expected
