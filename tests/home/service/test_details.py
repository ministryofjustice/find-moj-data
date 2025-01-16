import pytest

from datahub_client.entities import (
    AccessInformation,
    Chart,
    CustomEntityProperties,
    Dashboard,
    Database,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    Governance,
    OwnerRef,
    RelationshipType,
    TagRef,
)
from home.service.details import (
    ChartDetailsService,
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
    _parse_parent,
    is_access_requirements_a_url,
)
from home.urns import PlatformUrns
from tests.conftest import (
    generate_chart_metadata,
    generate_dashboard_metadata,
    generate_database_metadata,
    generate_table_metadata,
)


@pytest.mark.parametrize(
    "input, expected_output",
    [
        (
            {
                RelationshipType.PARENT: [
                    EntitySummary(
                        entity_ref=EntityRef(urn="urn:li:db", display_name="db"),
                        description="test",
                        entity_type="database",
                        tags=[],
                    )
                ]
            },
            EntityRef(urn="urn:li:db", display_name="db"),
        ),
        ({}, None),
        (
            {
                RelationshipType.DATA_LINEAGE: [
                    EntitySummary(
                        entity_ref=EntityRef(urn="urn:li:db", display_name="db"),
                        description="test",
                        entity_type="database",
                        tags=[],
                    )
                ]
            },
            None,
        ),
    ],
)
def test_parse_parent(input, expected_output):
    result = _parse_parent(input)
    assert result == expected_output


@pytest.mark.parametrize(
    "input, expected_output",
    [
        ("122", False),
        ("https://test.gov.uk", True),
        ("https://test.gov.uk/data/#readme", True),
        ("http://test.co.uk", True),
        ("ftp.example.com/how-to-access.txt", False),
        ("Just some instructions", False),
        ("", False),
        (123, False),
        (None, False),
        (["https://test.gov.uk"], False),
    ],
)
def test_is_access_requirements_a_url(input, expected_output):
    result = is_access_requirements_a_url(input)
    assert result == expected_output


class TestDatasetDetailsService:
    def test_get_context_contains_table_metadata(self, dataset_with_parent):
        service = DatasetDetailsService(dataset_with_parent["urn"])
        context = service.context
        assert context["entity"] == dataset_with_parent["table_metadata"]

    def test_get_context_contains_parent(self, mock_catalogue):
        parent = {
            RelationshipType.PARENT: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:container:parent", display_name="parent"
                    ),
                    description="",
                    tags=[],
                    entity_type="DATABASE",
                )
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
        assert context["entity"].custom_properties == custom_properties
        assert (
            context[
                "entity"
            ].custom_properties.further_information.dc_slack_channel_name
            == "test"
        )


class TestDatabaseDetailsService:

    def test_get_context_database(self, mock_catalogue, example_database):
        """
        Tests that the context contains the database metadata returned by the
        mock catalogue.
        """
        mock_database_name = "example_database"

        service = DatabaseDetailsService(mock_database_name)
        context = service.context
        assert context["entity"] == example_database

    def test_get_context_contains_slack(self, mock_catalogue):
        """
        Tests that the context contains the slack channel name and URL
        from the custom properties of the database
        """
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

        assert context["entity"].custom_properties == custom_properties
        assert (
            context[
                "entity"
            ].custom_properties.further_information.dc_slack_channel_name
            == "test"
        )

    def test_database_entities_in_context(self, example_database: Database):
        service = DatabaseDetailsService("example_database")
        context = service.context

        expected = example_database.relationships[RelationshipType.CHILD]

        assert context["tables"] == expected


class TestChartDetailsService:
    def test_get_context(self, mock_catalogue):
        chart_metadata = Chart(
            urn="urn:li:chart:(justice-data,test)",
            name="test",
            display_name="test",
            fully_qualified_name="test",
            description="test",
            external_url="https://www.test.com",
            subject_areas=[TagRef(urn="LAA", display_name="LAA")],
            governance=Governance(
                data_owner=OwnerRef(display_name="", email="lorem@ipsum.com", urn=""),
                data_stewards=[
                    OwnerRef(display_name="", email="lorem@ipsum.com", urn="")
                ],
            ),
            platform=EntityRef(urn="", display_name="justice-data"),
        )
        mock_catalogue.get_chart_details.return_value = chart_metadata

        context = ChartDetailsService("urn").context
        expected = {
            "entity": chart_metadata,
            "entity_type": "Chart",
            "platform_name": "Justice Data",
            "parent_entity": None,
            "parent_type": "dashboard",
            "h1_value": "test",
            "is_access_requirements_a_url": False,
            "PlatformUrns": PlatformUrns,
        }

        assert context == expected

    def test_get_context_contains_parent(self, mock_catalogue):
        parent = {
            RelationshipType.PARENT: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:container:parent", display_name="parent"
                    ),
                    description="",
                    tags=[],
                    entity_type="DASHBOARD",
                )
            ],
        }
        mock_chart = generate_chart_metadata(relations=parent)
        mock_catalogue.get_chart_details.return_value = mock_chart

        service = ChartDetailsService("urn:li:chart:test")
        context = service.context
        assert context["parent_entity"] == EntityRef(
            urn="urn:li:container:parent", display_name="parent"
        )


class TestDashboardDetailsService:
    def test_get_context_dashboard(self, mock_catalogue, example_dashboard: Dashboard):
        """
        Tests that the context contains the dashboard metadata returned by the
        mock catalogue.
        """
        mock_dashboard_name = "example_dashboard"

        service = DashboardDetailsService(mock_dashboard_name)
        context = service.context
        assert context["entity"] == example_dashboard

    def test_chart_entities_in_context(self, example_dashboard: Dashboard):
        service = DashboardDetailsService("example_dashboard")
        context = service.context

        expected = example_dashboard.relationships[RelationshipType.CHILD]

        assert context["charts"] == expected

    def test_custom_properties_in_context(self, mock_catalogue):
        custom_properties = CustomEntityProperties(
            access_information=AccessInformation(
                dc_access_requirements="This is a test there's nothing to access"
            )
        )
        mock_dashboard_name = "urn:li:dashboard:fake"
        mock_dashboard_metadata = generate_dashboard_metadata(
            name=mock_dashboard_name, custom_properties=custom_properties
        )
        mock_catalogue.get_dashboard_details.return_value = mock_dashboard_metadata

        service = DashboardDetailsService(mock_dashboard_name)
        context = service.context

        assert context["entity"].custom_properties == custom_properties
