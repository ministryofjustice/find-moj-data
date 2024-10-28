from datetime import datetime, timezone

import pytest

from data_platform_catalogue.client.graphql_helpers import (
    DATA_CUSTODIAN,
    _make_user_email_from_urn,
    parse_columns,
    parse_created_and_modified,
    parse_glossary_terms,
    parse_owner,
    parse_owners,
    parse_properties,
    parse_relations,
    parse_subtypes,
    parse_tags,
)
from data_platform_catalogue.entities import (
    AccessInformation,
    Column,
    ColumnRef,
    CustomEntityProperties,
    DataSummary,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    GlossaryTermRef,
    OwnerRef,
    RelationshipType,
    TagRef,
    UsageRestrictions,
)


def test_parse_columns_with_primary_key_and_foreign_key():
    entity = {
        "schemaMetadata": {
            "fields": [
                {
                    "fieldPath": "urn",
                    "label": None,
                    "nullable": False,
                    "description": "The primary identifier for the dataset entity.",
                    "type": "STRING",
                    "nativeDataType": "string",
                },
                {
                    "fieldPath": "upstream.upstreamLineage",
                    "label": None,
                    "nullable": False,
                    "description": "Upstream lineage of a dataset",
                    "type": "STRUCT",
                    "nativeDataType": "upstreamLineage",
                },
            ],
            "primaryKeys": ["urn"],
            "foreignKeys": [
                {
                    "name": "DownstreamOf",
                    "foreignFields": [{"fieldPath": "urn"}],
                    "foreignDataset": {
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)",
                        "properties": {"name": "Dataset", "qualifiedName": None},
                    },
                    "sourceFields": [{"fieldPath": "upstream.upstreamLineage"}],
                }
            ],
        }
    }

    assert parse_columns(entity) == [
        Column(
            name="urn",
            display_name="urn",
            type="string",
            description="The primary identifier for the dataset entity.",
            nullable=False,
            is_primary_key=True,
            foreign_keys=[],
        ),
        Column(
            name="upstream.upstreamLineage",
            display_name="upstreamLineage",
            type="upstreamLineage",
            description="Upstream lineage of a dataset",
            nullable=False,
            is_primary_key=False,
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
    ]


def test_parse_columns_with_no_keys():
    entity = {
        "schemaMetadata": {
            "fields": [
                {
                    "fieldPath": "urn",
                    "label": None,
                    "nullable": False,
                    "description": "The primary identifier for the dataset entity.",
                    "type": "STRING",
                    "nativeDataType": "string",
                },
                {
                    "fieldPath": "upstreamLineage",
                    "label": None,
                    "nullable": False,
                    "description": "Upstream lineage of a dataset",
                    "type": "STRUCT",
                    "nativeDataType": "upstreamLineage",
                },
            ],
            "primaryKeys": [],
            "foreignKeys": [],
        }
    }

    assert parse_columns(entity) == [
        Column(
            name="upstreamLineage",
            display_name="upstreamLineage",
            type="upstreamLineage",
            description="Upstream lineage of a dataset",
            nullable=False,
            is_primary_key=False,
            foreign_keys=[],
        ),
        Column(
            name="urn",
            display_name="urn",
            type="string",
            description="The primary identifier for the dataset entity.",
            nullable=False,
            is_primary_key=False,
            foreign_keys=[],
        ),
    ]


def test_parse_columns_with_null_descriptions():
    entity = {
        "schemaMetadata": {
            "fields": [
                {
                    "fieldPath": "urn",
                    "label": None,
                    "nullable": False,
                    "description": None,
                    "type": "STRING",
                    "nativeDataType": "string",
                }
            ],
            "primaryKeys": [],
            "foreignKeys": [],
        }
    }

    assert parse_columns(entity) == [
        Column(
            name="urn",
            display_name="urn",
            type="string",
            description="",
            nullable=False,
            is_primary_key=False,
            foreign_keys=[],
        )
    ]


def test_parse_columns_with_no_schema():
    entity = {}

    assert parse_columns(entity) == []
    assert parse_columns(entity) == []


def test_parse_relations():
    relations = {
        "relationships": {
            "total": 1,
            "relationships": [
                {
                    "entity": {
                        "urn": "urn:li:dataProduct:test",
                        "type": "DATA_PRODUCT",
                        "properties": {"name": "test", "description": "a test entity"},
                        "tags": {
                            "tags": [
                                {"tag": {"urn": "urn:li:tag:dc_display_in_catalogue"}}
                            ]
                        },
                    }
                }
            ],
        }
    }
    result = parse_relations(RelationshipType.PARENT, [relations["relationships"]])
    assert result == {
        RelationshipType.PARENT: [
            EntitySummary(
                entity_ref=EntityRef(
                    urn="urn:li:dataProduct:test", display_name="test"
                ),
                description="a test entity",
                entity_type="DATA_PRODUCT",
                tags=[
                    TagRef(
                        urn="urn:li:tag:dc_display_in_catalogue",
                        display_name="dc_display_in_catalogue",
                    )
                ],
            )
        ]
    }


def test_parse_relations_blank():
    relations = {"relationships": {"total": 0, "relationships": []}}
    result = parse_relations(RelationshipType.PARENT, [relations["relationships"]])
    assert result == {RelationshipType.PARENT: []}


@pytest.mark.parametrize(
    "raw_created,raw_last_modified,expected_created,expected_modified",
    [
        (
            1710426920000,
            {"time": 1710426921000, "actor": "Shakira"},
            datetime(2024, 3, 14, 14, 35, 20, tzinfo=timezone.utc),
            datetime(2024, 3, 14, 14, 35, 21, tzinfo=timezone.utc),
        ),
        (
            0,
            {"time": 0, "actor": "Shakira"},
            None,
            None,
        ),
        (
            None,
            None,
            None,
            None,
        ),
    ],
)
def test_parse_created_and_modified(
    raw_created, raw_last_modified, expected_created, expected_modified
):
    properties = {
        "created": raw_created,
        "lastModified": raw_last_modified,
    }

    created, modified = parse_created_and_modified(properties)

    assert created == expected_created
    assert modified == expected_modified


def test_parse_properties():
    entity = {
        "properties": {
            "customProperties": [
                {"key": "dpia_required", "value": False},
                {"key": "dpia_location", "value": ""},
                {"key": "data_sensitivity_level", "value": "OFFICIAL"},
                {"key": "dc_where_to_access_dataset", "value": "analytical_platform"},
                {"key": "dc_slack_channel_name", "value": "test-channel"},
                {"key": "dc_slack_channel_url", "value": "test-url"},
                {"key": "source_dataset_name", "value": ""},
                {"key": "s3_location", "value": "s3://databucket/"},
                {"key": "row_count", "value": 100},
                {"key": "Not_IN", "value": "dddd"},
            ],
            "name": "test",
            "description": "test description",
        },
        "editableProperties": {"edit1": "q"},
    }
    properties, custom_properties = parse_properties(entity)

    assert properties == {
        "name": "test",
        "description": "test description",
        "edit1": "q",
    }

    assert custom_properties == CustomEntityProperties(
        usage_restrictions=UsageRestrictions(
            dpia_required=False,
            dpia_location="",
        ),
        access_information=AccessInformation(
            dc_where_to_access_dataset="analytical_platform",
            source_dataset_name="",
            s3_location="s3://databucket/",
        ),
        data_summary=DataSummary(row_count=100),
        further_information=FurtherInformation(
            dc_slack_channel_name="test-channel", dc_slack_channel_url="test-url"
        ),
    )


def test_parse_properties_with_none_values():
    entity = {
        "properties": {
            "customProperties": [
                {"key": "dpia_required", "value": False},
                {"key": "dpia_location", "value": ""},
                {"key": "data_sensitivity_level", "value": "OFFICIAL"},
                {"key": "dc_where_to_access_dataset", "value": "analytical_platform"},
                {"key": "source_dataset_name", "value": ""},
                {"key": "s3_location", "value": "s3://databucket/"},
                {"key": "row_count", "value": 100},
                {"key": "Not_IN", "value": "dddd"},
            ],
            "name": "test",
            "description": None,
            "externalUrl": None,
        },
        "editableProperties": {"edit1": "q"},
    }
    properties, custom_properties = parse_properties(entity)

    assert properties == {
        "name": "test",
        "description": "",
        "edit1": "q",
        "externalUrl": "",
    }

    assert custom_properties == CustomEntityProperties(
        usage_restrictions=UsageRestrictions(
            dpia_required=False,
            dpia_location="",
        ),
        access_information=AccessInformation(
            dc_where_to_access_dataset="analytical_platform",
            source_dataset_name="",
            s3_location="s3://databucket/",
        ),
        data_summary=DataSummary(row_count=100),
        further_information=FurtherInformation(),
    )


def test_parse_columns_with_empty_fields():
    entity = {
        "schemaMetadata": {
            "fields": [],
            "primaryKeys": [],
            "foreignKeys": [],
        }
    }

    assert parse_columns(entity) == []


def test_parse_columns_with_unrecognized_type():
    entity = {
        "schemaMetadata": {
            "fields": [
                {
                    "fieldPath": "unknownField",
                    "label": None,
                    "nullable": True,
                    "description": "An unknown field type",
                    "type": "UNKNOWN_TYPE",
                    "nativeDataType": "unknown",
                }
            ],
            "primaryKeys": [],
            "foreignKeys": [],
        }
    }

    assert parse_columns(entity) == [
        Column(
            name="unknownField",
            display_name="unknownField",
            type="unknown",
            description="An unknown field type",
            nullable=True,
            is_primary_key=False,
            foreign_keys=[],
        )
    ]


def test_parse_relations_multiple_relationships():
    relations = {
        "relationships": {
            "total": 2,
            "relationships": [
                {
                    "entity": {
                        "urn": "urn:li:dataProduct:test1",
                        "type": "DATA_PRODUCT",
                        "properties": {
                            "name": "test1",
                            "description": "first test entity",
                        },
                        "tags": {
                            "tags": [
                                {"tag": {"urn": "urn:li:tag:dc_display_in_catalogue"}}
                            ]
                        },
                    }
                },
                {
                    "entity": {
                        "urn": "urn:li:dataProduct:test2",
                        "type": "DATA_PRODUCT",
                        "properties": {
                            "name": "test2",
                            "description": "second test entity",
                        },
                        "tags": {
                            "tags": [
                                {"tag": {"urn": "urn:li:tag:dc_display_in_catalogue2"}}
                            ]
                        },
                    }
                },
            ],
        }
    }
    result = parse_relations(RelationshipType.PARENT, [relations["relationships"]])
    assert result == {
        RelationshipType.PARENT: [
            EntitySummary(
                entity_ref=EntityRef(
                    urn="urn:li:dataProduct:test1", display_name="test1"
                ),
                description="first test entity",
                entity_type="DATA_PRODUCT",
                tags=[
                    TagRef(
                        urn="urn:li:tag:dc_display_in_catalogue",
                        display_name="dc_display_in_catalogue",
                    )
                ],
            ),
            EntitySummary(
                entity_ref=EntityRef(
                    urn="urn:li:dataProduct:test2", display_name="test2"
                ),
                description="second test entity",
                entity_type="DATA_PRODUCT",
                tags=[
                    TagRef(
                        urn="urn:li:tag:dc_display_in_catalogue2",
                        display_name="dc_display_in_catalogue2",
                    )
                ],
            ),
        ]
    }


def test_parse_tags():
    tag = TagRef(display_name="abc", urn="urn:tag:abc")
    result = parse_tags(
        {
            "tags": {
                "tags": [
                    {
                        "tag": {
                            "urn": tag.urn,
                            "properties": {
                                "name": tag.display_name,
                            },
                        }
                    }
                ]
            }
        }
    )

    assert result == [tag]


def test_parse_glossary_terms():
    term = GlossaryTermRef(
        display_name="abc", urn="urn:glossaryTerm:abc", description="hello world"
    )
    result = parse_glossary_terms(
        {
            "glossaryTerms": {
                "terms": [
                    {
                        "term": {
                            "urn": term.urn,
                            "properties": {
                                "name": term.display_name,
                                "description": term.description,
                            },
                        }
                    }
                ]
            }
        }
    )

    assert result == [term]


@pytest.mark.parametrize(
    "urn, expected_email",
    [
        (
            "urn:li:corpuser:jon.smith",
            "jon.smith@justice.gov.uk",
        ),
        (
            "urn:li:corpuser:jon.smith54",
            "jon.smith54@justice.gov.uk",
        ),
        (
            "urn:li:corpuser:jon.smith.sullivan",
            "jon.smith.sullivan@justice.gov.uk",
        ),
    ],
)
def test_make_user_email_from_urn(urn, expected_email):
    email = _make_user_email_from_urn(urn)
    assert email == expected_email


def test_parse_subtypes():
    result = parse_subtypes({"subTypes": {"typeNames": ["abc", "def"]}})

    assert result == ["abc", "def"]


def test_parse_missing_subtypes():
    result = parse_subtypes({"subTypes": None})

    assert result == []


def test_parse_owner_of_wrong_type():
    entity = {
        "ownership": {
            "owners": [
                {
                    "owner": {"urn": "urn:li:corpuser:joe.bloggs", "properties": None},
                    "ownershipType": {
                        "urn": "urn:li:ownershipType:__system__dataowner",
                        "type": "CUSTOM_OWNERSHIP_TYPE",
                        "info": None,
                    },
                }
            ]
        }
    }

    owner = parse_owner(entity, ownership_type_urn="urn:li:ownershipType:chiefMouser")
    assert owner == OwnerRef(display_name="", email="", urn="")


def test_parse_owner_without_account():
    entity = {
        "ownership": {
            "owners": [
                {
                    "owner": {"urn": "urn:li:corpuser:joe.bloggs", "properties": None},
                    "ownershipType": {
                        "urn": "urn:li:ownershipType:__system__dataowner",
                        "type": "CUSTOM_OWNERSHIP_TYPE",
                        "info": None,
                    },
                }
            ]
        }
    }
    owner = parse_owner(entity)
    assert owner.email == "joe.bloggs@justice.gov.uk"


def test_parse_owner_with_account():
    entity = {
        "ownership": {
            "owners": [
                {
                    "owner": {
                        "urn": "urn:li:corpuser:joe.bloggs",
                        "properties": {
                            "fullName": "Joe Bloggs",
                            "email": "joeseph.bloggerson-bloggs@justice.gov.uk",
                        },
                    },
                    "ownershipType": {
                        "urn": "urn:li:ownershipType:__system__dataowner",
                        "type": "CUSTOM_OWNERSHIP_TYPE",
                        "info": None,
                    },
                }
            ]
        }
    }
    owner = parse_owner(entity)
    assert owner.email == "joeseph.bloggerson-bloggs@justice.gov.uk"


def test_parse_owners():
    entity = {
        "ownership": {
            "owners": [
                {
                    "owner": {
                        "urn": "urn:li:corpuser:word.smith",
                        "properties": None,
                    },
                    "ownershipType": {
                        "urn": "urn:li:ownershipType:data_custodian",
                        "type": "CUSTOM_OWNERSHIP_TYPE",
                    },
                },
                {
                    "owner": {
                        "urn": "urn:li:corpuser:mo.numbers",
                        "properties": None,
                    },
                    "ownershipType": {
                        "urn": "urn:li:ownershipType:data_custodian",
                        "type": "CUSTOM_OWNERSHIP_TYPE",
                    },
                },
            ]
        }
    }
    owners = parse_owners(entity, ownership_type_urn=DATA_CUSTODIAN)
    assert owners == [
        OwnerRef(
            urn="urn:li:corpuser:word.smith",
            email="word.smith@justice.gov.uk",
            display_name="",
        ),
        OwnerRef(
            urn="urn:li:corpuser:mo.numbers",
            email="mo.numbers@justice.gov.uk",
            display_name="",
        ),
    ]
