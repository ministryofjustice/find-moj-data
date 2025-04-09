from unittest.mock import MagicMock

from datahub_client.entities import (
    Column,
    ColumnQualityMetrics,
    EntityRef,
    EntitySummary,
)
from home.service.details import (
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
)
from home.service.details_csv import (
    DashboardDetailsCsvFormatter,
    DatabaseDetailsCsvFormatter,
    DatasetDetailsCsvFormatter,
)


def test_dataset_details_csv_formatter(example_table):
    details_service = MagicMock(spec=DatasetDetailsService)
    columns = [
        Column(
            name="foo",
            display_name="Foo",
            type="string",
            description="an example",
            nullable=False,
            is_primary_key=True,
            quality_metrics=ColumnQualityMetrics(),
        ),
        Column(
            name="bar",
            display_name="Bar",
            type="integer",
            description="another example",
            nullable=True,
            is_primary_key=False,
            quality_metrics=ColumnQualityMetrics(),
        ),
    ]
    details_service.table_metadata = example_table
    example_table.column_details = columns
    csv_formatter = DatasetDetailsCsvFormatter(details_service)

    assert csv_formatter.headers() == [
        "name",
        "display_name",
        "type",
        "description",
    ]
    assert csv_formatter.data() == [
        (
            "foo",
            "Foo",
            "string",
            "an example",
        ),
        (
            "bar",
            "Bar",
            "integer",
            "another example",
        ),
    ]


def test_database_details_csv_formatter(example_database):
    tables = [
        EntitySummary(
            entity_ref=EntityRef(display_name="foo", urn="urn:foo"),
            description="an example",
            entity_type="Table",
            tags=[],
        ),
        EntitySummary(
            entity_ref=EntityRef(display_name="bar", urn="urn:bar"),
            description="another example",
            entity_type="Table",
            tags=[],
        ),
    ]

    details_service = MagicMock(spec=DatabaseDetailsService)
    details_service.entities_in_database = tables

    csv_formatter = DatabaseDetailsCsvFormatter(details_service)

    assert csv_formatter.headers() == ["urn", "display_name", "description"]
    assert csv_formatter.data() == [
        ("urn:foo", "foo", "an example"),
        ("urn:bar", "bar", "another example"),
    ]


def test_dashboard_details_csv_formatter(example_dashboard):
    charts = [
        EntitySummary(
            entity_ref=EntityRef(display_name="foo", urn="urn:foo"),
            description="an example",
            entity_type="Chart",
            tags=[],
        ),
        EntitySummary(
            entity_ref=EntityRef(display_name="bar", urn="urn:bar"),
            description="another example",
            entity_type="Chart",
            tags=[],
        ),
    ]

    details_service = MagicMock(spec=DashboardDetailsService)
    details_service.children = charts

    csv_formatter = DashboardDetailsCsvFormatter(details_service)

    assert csv_formatter.headers() == ["urn", "display_name", "description"]
    assert csv_formatter.data() == [
        ("urn:foo", "foo", "an example"),
        ("urn:bar", "bar", "another example"),
    ]
