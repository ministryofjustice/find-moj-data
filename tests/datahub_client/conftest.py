from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest
from datahub.metadata.schema_classes import DomainPropertiesClass

from datahub_client.entities import (
    AccessInformation,
    CustomEntityProperties,
    DataSummary,
    DomainRef,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    GlossaryTermRef,
    Governance,
    OwnerRef,
    RelationshipType,
    TagRef,
    UsageRestrictions,
)

from .test_helpers.graph_helpers import MockDataHubGraph
from .test_helpers.mce_helpers import check_golden_file

FROZEN_TIME = "2023-04-14 07:00:00"


@pytest.fixture
def base_entity_metadata():
    return {
        "urn:li:domain:LAA": {
            "domainProperties": DomainPropertiesClass(
                name="LAA", description="Legal Aid Authority"
            )
        }
    }


@pytest.fixture
def base_mock_graph(
    base_entity_metadata: Dict[str, Dict[str, Any]]
) -> MockDataHubGraph:
    return MockDataHubGraph(entity_graph=base_entity_metadata)


@pytest.fixture
def test_snapshots_dir(pytestconfig: pytest.Config) -> Path:
    rootpath = Path(__file__).parent
    return rootpath / "snapshots"


@pytest.fixture
def check_snapshot(test_snapshots_dir, pytestconfig):
    def _check_snapshot(name: str, output_file: Path):
        last_snapshot = Path(test_snapshots_dir / name)
        check_golden_file(pytestconfig, output_file, last_snapshot)

    return _check_snapshot


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden-files",
        action="store_true",
        default=False,
    )
    parser.addoption("--copy-output-files", action="store_true", default=False)


@pytest.fixture
def entity_data_with_timestamps_in_future():
    future_timestamp = datetime.now() + timedelta(days=1)
    return {
        "urn": "urn:li:chart:(justice-data,absconds)",
        "display_name": "Absconds",
        "name": "Absconds",
        "fully_qualified_name": "",
        "description": "Number of absconds",
        "relationships": {
            RelationshipType.PARENT: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:database:example", display_name="example"
                    ),
                    description="entity for an example",
                    entity_type="DATABASE",
                    tags=[
                        TagRef(
                            urn="urn:li:tag:dc_display_in_catalogue",
                            display_name="dc_display_in_catalogue",
                        )
                    ],
                )
            ]
        },
        "domain": DomainRef(display_name="HMPPS", urn="urn:li:domain:HMCTS"),
        "governance": Governance(
            data_owner=OwnerRef(
                display_name="John Doe",
                email="jogn.doe@justice.gov.uk",
                urn="urn:li:corpuser:john.doe",
            ),
            data_stewards=[
                OwnerRef(
                    display_name="Jane Smith",
                    email="jane.smith@justice.gov.uk",
                    urn="urn:li:corpuser:jane.smith",
                )
            ],
            data_custodians=[
                OwnerRef(
                    display_name="Rosanne Columns",
                    email="rosanne.columns@justice.gov.uk",
                    urn="urn:li:corpuser:rosanne.columns",
                )
            ],
        ),
        "glossary_terms": [
            GlossaryTermRef(
                display_name="Essential Shared Data Asset (ESDA)",
                urn="urn:li:glossaryTerm:ESDA",
                description="An ESDA is...",
            )
        ],
        "metadata_last_ingested": future_timestamp,
        "created": future_timestamp,
        "data_last_modified": future_timestamp,
        "platform": EntityRef(urn="urn:li:dataPlatform:kafka", display_name="Kafka"),
        "custom_properties": CustomEntityProperties(
            usage_restrictions=UsageRestrictions(
                dpia_required=False, dpia_location="OneTrust"
            ),
            access_information=AccessInformation(
                dc_where_to_access_dataset="Analytical platform",
                source_dataset_name="stg_xhibit_bw_history",
                s3_location="s3://alpha-hmpps-reports-data",
                dc_access_requirements="Access granted on request",
            ),
            data_summary=DataSummary(row_count=123, refresh_period="Daily"),
            further_information=FurtherInformation(
                dc_slack_channel_name="#data-engineering",
                dc_slack_channel_url="https://hmpps-data-engineering.slack.com",
                dc_teams_channel_name="Data team",
                dc_teams_channel_url="https://teams.microsoft.com/l/channel/123",
                dc_team_email="best-data-team@justice.gov.uk",
            ),
        ),
        "tags_to_display": ["nomis", "data-warehouse"],
    }
