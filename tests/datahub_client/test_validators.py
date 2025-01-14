from datetime import datetime, timedelta

import pytest

from datahub_client.entities import (
    AccessInformation,
    CustomEntityProperties,
    DataSummary,
    DomainRef,
    Entity,
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


def test_entity_timestamps_in_future_validation():
    future_timestamp = datetime.now() + timedelta(days=1)
    entity_data_with_timestamps_in_future = {
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
    with pytest.raises(ValueError) as exc:
        Entity(**entity_data_with_timestamps_in_future)

    assert "timestamp must be in the past" in str(exc.value)
