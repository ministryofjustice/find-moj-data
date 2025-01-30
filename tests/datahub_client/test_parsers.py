import pytest

from datahub_client.entities import (
    AccessInformation,
    Chart,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Dashboard,
    Database,
    DatahubEntityType,
    DatahubSubtype,
    DataSummary,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    GlossaryTermRef,
    OwnerRef,
    PublicationCollection,
    PublicationDataset,
    RelationshipType,
    SecurityClassification,
    Table,
    TagRef,
    UsageRestrictions,
)
from datahub_client.parsers import (
    DATA_CUSTODIAN,
    ChartParser,
    DashboardParser,
    DatabaseParser,
    DatasetParser,
    EntityParser,
    EntityParserFactory,
    PublicationCollectionParser,
    PublicationDatasetParser,
    TableParser,
)
from datahub_client.search.search_types import SearchResult


@pytest.fixture
def mock_dataset_graphql_entity():
    return {
        "urn": "urn:li:dataset:test_dataset",
        "type": "DATASET",
        "properties": {
            "name": "Test Dataset",
            "description": "A test dataset for unit testing",
            "customProperties": [
                {"key": "dpia_required", "value": False},
                {"key": "dpia_location", "value": ""},
                {"key": "data_sensitivity_level", "value": "OFFICIAL"},
                {"key": "dc_where_to_access_dataset", "value": "analytical_platform"},
                {"key": "source_dataset_name", "value": ""},
                {"key": "s3_location", "value": "s3://databucket/"},
                {"key": "row_count", "value": 100},
                {
                    "key": "security_classification",
                    "value": SecurityClassification.OFFICIAL_SENSITIVE.value,
                },
                {"key": "refresh_period", "value": "Weekly"},
            ],
        },
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
            "primaryKeys": ["urn"],
            "foreignKeys": [
                {
                    "name": "DownstreamOf",
                    "foreignFields": [{"fieldPath": "urn"}],
                    "foreignDataset": {
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)",
                        "properties": {"name": "Dataset", "qualifiedName": None},
                    },
                    "sourceFields": [{"fieldPath": "upstreamLineage"}],
                }
            ],
        },
        "relationships": {
            "total": 1,
            "relationships": [
                {
                    "entity": {
                        "urn": "urn:li:container:test",
                        "type": "DATABASE",
                        "properties": {"name": "test", "description": "a test entity"},
                        "tags": {
                            "tags": [
                                {"tag": {"urn": "urn:li:tag:dc_display_in_catalogue"}}
                            ]
                        },
                    }
                }
            ],
        },
        "platform": {
            "name": "DataHub",
            "urn": "urn:li:dataPlatform:datahub",
        },
    }


@pytest.fixture
def mock_graphql_search_result(mock_dataset_graphql_entity):
    return {"entity": mock_dataset_graphql_entity, "matchedFields": []}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "parser, entity_object_type",
    [
        (DatasetParser(), Table),
        (TableParser(), Table),
        (ChartParser(), Chart),
        (DatabaseParser(), Database),
        (PublicationCollectionParser(), PublicationCollection),
        (PublicationDatasetParser(), PublicationDataset),
        (DashboardParser(), Dashboard),
    ],
)
class TestParsers:
    def test_parse(self, parser, entity_object_type, mock_graphql_search_result):
        search_result = parser.parse(mock_graphql_search_result)
        assert isinstance(search_result, SearchResult)
        assert search_result.urn == mock_graphql_search_result["entity"]["urn"]

    def test_parse_to_entity_object(
        self, parser, entity_object_type, mock_dataset_graphql_entity
    ):
        urn = "urn:li:dataset:test_dataset"
        table = parser.parse_to_entity_object(mock_dataset_graphql_entity, urn)
        assert isinstance(table, entity_object_type)
        assert table.urn == urn


class TestEntityParser:
    @pytest.fixture
    def parser(self):
        return EntityParser()

    def test_parse_columns_with_primary_key_and_foreign_key(self, parser):
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

        assert parser.parse_columns(entity) == [
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

    def test_parse_columns_with_no_keys(self, parser):
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

        assert parser.parse_columns(entity) == [
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

    def test_parse_columns_with_null_descriptions(self, parser):
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

        assert parser.parse_columns(entity) == [
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

    def test_parse_columns_with_no_schema(self, parser):
        entity = {}

        assert parser.parse_columns(entity) == []
        assert parser.parse_columns(entity) == []

    def test_parse_relations(self, parser):
        relations = {
            "relationships": {
                "total": 1,
                "relationships": [
                    {
                        "entity": {
                            "urn": "urn:li:dataProduct:test",
                            "type": "DATA_PRODUCT",
                            "properties": {
                                "name": "test",
                                "description": "a test entity",
                            },
                            "tags": {
                                "tags": [
                                    {
                                        "tag": {
                                            "urn": "urn:li:tag:dc_display_in_catalogue"
                                        }
                                    }
                                ]
                            },
                        }
                    }
                ],
            }
        }
        result = parser.parse_relations(
            RelationshipType.PARENT, [relations["relationships"]]
        )
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

    def test_parse_relations_blank(self, parser):
        relations = {"relationships": {"total": 0, "relationships": []}}
        result = parser.parse_relations(
            RelationshipType.PARENT, [relations["relationships"]]
        )
        assert result == {RelationshipType.PARENT: []}

    @pytest.mark.parametrize(
        "raw_created,raw_last_modified,expected_created,expected_modified",
        [
            (
                1710426920000,
                {"time": 1710426921000, "actor": "Shakira"},
                1710426920000,
                1710426921000,
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
        self,
        parser,
        raw_created,
        raw_last_modified,
        expected_created,
        expected_modified,
    ):
        properties = {
            "created": raw_created,
            "lastModified": raw_last_modified,
        }

        created = parser.parse_data_created(properties)
        modified = parser.parse_data_last_modified(properties)

        assert created == expected_created
        assert modified == expected_modified

    def test_parse_properties(self, parser):
        entity = {
            "properties": {
                "customProperties": [
                    {"key": "dpia_required", "value": False},
                    {"key": "dpia_location", "value": ""},
                    {"key": "data_sensitivity_level", "value": "OFFICIAL"},
                    {
                        "key": "dc_where_to_access_dataset",
                        "value": "analytical_platform",
                    },
                    {"key": "dc_slack_channel_name", "value": "test-channel"},
                    {"key": "dc_slack_channel_url", "value": "test-url"},
                    {"key": "source_dataset_name", "value": ""},
                    {"key": "s3_location", "value": "s3://databucket/"},
                    {"key": "row_count", "value": 100},
                    {"key": "Not_IN", "value": "dddd"},
                    {
                        "key": "security_classification",
                        "value": SecurityClassification.OFFICIAL_SENSITIVE.value,
                    },
                    {"key": "refresh_period", "value": "Weekly"},
                ],
                "name": "test",
                "description": "test description",
            },
            "editableProperties": {"edit1": "q"},
        }
        properties, custom_properties = parser.parse_properties(entity)

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
            data_summary=DataSummary(row_count=100, refresh_period="Weekly"),
            further_information=FurtherInformation(
                dc_slack_channel_name="test-channel", dc_slack_channel_url="test-url"
            ),
            security_classification=SecurityClassification.OFFICIAL_SENSITIVE,
        )

    def test_parse_properties_with_none_values(self, parser):
        entity = {
            "properties": {
                "customProperties": [
                    {"key": "dpia_required", "value": False},
                    {"key": "dpia_location", "value": ""},
                    {"key": "data_sensitivity_level", "value": "OFFICIAL"},
                    {
                        "key": "dc_where_to_access_dataset",
                        "value": "analytical_platform",
                    },
                    {"key": "source_dataset_name", "value": ""},
                    {"key": "s3_location", "value": "s3://databucket/"},
                    {"key": "row_count", "value": 100},
                    {"key": "Not_IN", "value": "dddd"},
                    {
                        "key": "security_classification",
                        "value": SecurityClassification.OFFICIAL_SENSITIVE.value,
                    },
                ],
                "name": "test",
                "description": None,
                "externalUrl": None,
            },
            "editableProperties": {"edit1": "q"},
        }
        properties, custom_properties = parser.parse_properties(entity)

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
            security_classification=SecurityClassification.OFFICIAL_SENSITIVE,
        )

    def test_parse_columns_with_empty_fields(self, parser):
        entity = {
            "schemaMetadata": {
                "fields": [],
                "primaryKeys": [],
                "foreignKeys": [],
            }
        }

        assert parser.parse_columns(entity) == []

    def test_parse_columns_with_unrecognized_type(self, parser):
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

        assert parser.parse_columns(entity) == [
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

    def test_parse_relations_multiple_relationships(self, parser):
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
                                    {
                                        "tag": {
                                            "urn": "urn:li:tag:dc_display_in_catalogue"
                                        }
                                    }
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
                                    {
                                        "tag": {
                                            "urn": "urn:li:tag:dc_display_in_catalogue2"
                                        }
                                    }
                                ]
                            },
                        }
                    },
                ],
            }
        }
        result = parser.parse_relations(
            RelationshipType.PARENT, [relations["relationships"]]
        )
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

    def test_parse_tags(self, parser):
        tag = TagRef(display_name="abc", urn="urn:tag:abc")
        result = parser.parse_tags(
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

    def test_parse_glossary_terms(self, parser):
        term = GlossaryTermRef(
            display_name="abc", urn="urn:glossaryTerm:abc", description="hello world"
        )
        result = parser.parse_glossary_terms(
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
    def test_make_user_email_from_urn(self, parser, urn, expected_email):
        email = parser._make_user_email_from_urn(urn)
        assert email == expected_email

    def test_parse_subtypes(self, parser):
        result = parser.parse_subtypes({"subTypes": {"typeNames": ["abc", "def"]}})

        assert result == ["abc", "def"]

    def test_parse_missing_subtypes(self, parser):
        result = parser.parse_subtypes({"subTypes": None})

        assert result == []

    def test_parse_owner_without_account(self, parser):
        entity = {
            "ownership": {
                "owners": [
                    {
                        "owner": {
                            "urn": "urn:li:corpuser:joe.bloggs",
                            "properties": None,
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
        owner = parser.parse_data_owner(entity)
        assert owner.email == "joe.bloggs@justice.gov.uk"

    def test_parse_owner_with_account(self, parser):
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
        owner = parser.parse_data_owner(entity)
        assert owner.email == "joeseph.bloggerson-bloggs@justice.gov.uk"

    def test_parse_owners(self, parser):
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
        owners = parser._parse_owners_by_type(entity, ownership_type_urn=DATA_CUSTODIAN)
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

    def test_parse_updated(self, parser):
        expected_timestamp = 12345678
        example_with_updated = {
            "runs": {"runs": [{"created": {"time": expected_timestamp}}]}
        }
        example_no_updated = {}

        assert (
            parser.parse_last_datajob_run_date(example_with_updated)
            == expected_timestamp
        )
        assert parser.parse_last_datajob_run_date(example_no_updated) is None

    @pytest.mark.parametrize(
        "tags, expected_refresh_period",
        [
            ([TagRef(display_name="daily_opg", urn="urn:li:tag:daily_opg")], "Daily"),
            ([TagRef(display_name="monthly", urn="urn:li:tag:monthly")], "Monthly"),
            ([TagRef(display_name="dc_cadet", urn="urn:li:tag:dc_cadet")], ""),
            (
                [
                    TagRef(display_name="daily", urn="urn:li:tag:dc_cadet"),
                    TagRef(display_name="monthly", urn="urn:li:tag:dc_cadet"),
                ],
                "Daily, monthly",
            ),
        ],
    )
    def test_get_refresh_period_from_cadet_tags(
        self, parser, tags, expected_refresh_period
    ):
        refresh_period = parser.get_refresh_period_from_cadet_tags(tags)
        assert refresh_period == expected_refresh_period


class TestEntityParserFactory:
    @pytest.fixture
    def parser_factory(self):
        return EntityParserFactory()

    @pytest.mark.parametrize(
        "entity_slug, expected_parser",
        [
            ({"entity": {"type": DatahubEntityType.DATASET.value}}, TableParser),
            (
                {
                    "entity": {
                        "type": DatahubEntityType.DATASET.value,
                        "subTypes": {
                            "typeNames": [DatahubSubtype.PUBLICATION_DATASET.value]
                        },
                    }
                },
                PublicationDatasetParser,
            ),
            ({"entity": {"type": DatahubEntityType.CHART.value}}, ChartParser),
            ({"entity": {"type": DatahubEntityType.DASHBOARD.value}}, DashboardParser),
            ({"entity": {"type": DatahubEntityType.CONTAINER.value}}, DatabaseParser),
            (
                {
                    "entity": {
                        "type": DatahubEntityType.CONTAINER.value,
                        "subTypes": {
                            "typeNames": [DatahubSubtype.PUBLICATION_COLLECTION.value]
                        },
                    }
                },
                PublicationCollectionParser,
            ),
        ],
    )
    def test_get_parser_for_entity_type(
        self, parser_factory, entity_slug, expected_parser
    ):
        parser = parser_factory.get_parser(entity_slug)
        assert isinstance(parser, expected_parser)
