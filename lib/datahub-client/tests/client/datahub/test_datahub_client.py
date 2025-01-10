from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from data_platform_catalogue.client.datahub_client import (
    DataHubCatalogueClient,
    InvalidDomain,
)
from data_platform_catalogue.client.exceptions import (
    EntityDoesNotExist,
    ReferencedEntityMissing,
)
from data_platform_catalogue.entities import (
    AccessInformation,
    Audience,
    Chart,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Database,
    DataSummary,
    DomainRef,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    Governance,
    OwnerRef,
    PublicationCollection,
    RelationshipType,
    Table,
    TagRef,
    UsageRestrictions,
)


class TestCatalogueClientWithDatahub:
    """
    Test that the contract with DataHubGraph has not changed, using a mock.

    If this is the case, then the final metadata graph should match a snapshot we took earlier.
    """

    @pytest.fixture
    def database(self):
        return Database(
            urn=None,
            name="my_database",
            display_name="my_database",
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
            relationships={
                RelationshipType.CHILD: [
                    EntitySummary(
                        entity_ref=EntityRef(
                            urn="urn:li:dataset:fake_table", display_name="fake_table"
                        ),
                        description="table description",
                        tags=[
                            TagRef(
                                display_name="some-tag",
                                urn="urn:li:tag:dc_display_in_catalogue",
                            )
                        ],
                        entity_type="TABLE",
                    )
                ]
            },
            metadata_last_ingested=1710426920000,
            created=1710426920000,
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
                further_information=FurtherInformation(
                    dc_slack_channel_name="test-channel",
                    dc_slack_channel_url="test-url",
                ),
            ),
        )

    @pytest.fixture
    def table(self):
        return Table(
            urn=None,
            display_name="Foo.Dataset",
            name="Dataset",
            fully_qualified_name="Foo.Dataset",
            description="Dataset",
            relationships={
                RelationshipType.PARENT: [
                    EntitySummary(
                        entity_ref=EntityRef(
                            urn="urn:li:container:my_database", display_name="database"
                        ),
                        description="db description",
                        tags=[
                            TagRef(
                                display_name="some-tag",
                                urn="urn:li:tag:dc_display_in_catalogue",
                            )
                        ],
                        entity_type="CONTAINER",
                    )
                ]
            },
            domain=DomainRef(display_name="LAA", urn="LAA"),
            governance=Governance(
                data_owner=OwnerRef(
                    display_name="", email="", urn=""
                ),
                data_stewards=[
                    OwnerRef(
                        display_name="", email="", urn=""
                    )
                ],
            ),
            tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
            metadata_last_ingested=1710426920000,
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
            custom_properties=CustomEntityProperties(
                access_information=AccessInformation(
                    dc_where_to_access_dataset="",
                    source_dataset_name="",
                    s3_location="",
                ),
                data_summary=DataSummary(row_count=5),
                usage_restrictions=UsageRestrictions(
                    dpia_required=True,
                    dpia_location="",
                ),
                further_information=FurtherInformation(
                    dc_slack_channel_name="test-channel",
                    dc_slack_channel_url="test-url",
                ),
            ),
        )

    @pytest.fixture
    def table2(self):
        return Table(
            urn=None,
            display_name="Foo.Dataset",
            name="Dataset",
            fully_qualified_name="Foo.Dataset",
            description="Dataset",
            relationships={
                RelationshipType.PARENT: [
                    EntityRef(
                        urn="urn:li:container:my_database", display_name="database"
                    )
                ]
            },
            domain=DomainRef(display_name="LAA", urn="LAA"),
            governance=Governance(
                data_owner=OwnerRef(
                    display_name="", email="", urn=""
                ),
                data_stewards=[
                    OwnerRef(
                        display_name="", email="", urn=""
                    )
                ],
            ),
            tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
            metadata_last_ingested=1710426920000,
            created=None,
            column_details=[
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
                    name="upstreamLineage",
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
            ],
            platform=EntityRef(urn="athena", display_name="athena"),
            custom_properties=CustomEntityProperties(
                access_information=AccessInformation(
                    dc_where_to_access_dataset="",
                    source_dataset_name="",
                    s3_location="",
                ),
                usage_restrictions=UsageRestrictions(
                    dpia_required=True,
                    dpia_location="",
                ),
                data_summary=DataSummary(row_count=5),
                further_information=FurtherInformation(
                    dc_slack_channel_name="test-channel",
                    dc_slack_channel_url="test-url",
                ),
            ),
        )

    @pytest.fixture
    def datahub_client(self, base_mock_graph) -> DataHubCatalogueClient:
        return DataHubCatalogueClient(
            jwt_token="abc", api_url="http://example.com/api/gms", graph=base_mock_graph
        )

    @pytest.fixture
    def golden_file_in_db(self):
        return Path(
            Path(__file__).parent / "../../test_resources/golden_database_in.json"
        )

    def test_get_dataset(
        self,
        datahub_client,
        base_mock_graph,
    ):
        urn = "abc"
        datahub_response = {
            "dataset": {
                "type": "DATASET",
                "platform": {"name": "datahub"},
                "ownership": None,
                "subTypes": None,
                "downstream_lineage_relations": {"total": 0, "relationships": []},
                "upstream_lineage_relations": {"total": 0, "relationships": []},
                "parent_container_relations": {
                    "total": 1,
                    "relationships": [
                        {
                            "type": "IsPartOf",
                            "direction": "OUTGOING",
                            "entity": {
                                "urn": "urn:li:container:database",
                                "type": "CONTAINER",
                                "subTypes": {"typeNames": ["Database"]},
                                "properties": {"name": "database"},
                                "tags": {
                                    "tags": [
                                        {
                                            "tag": {
                                                "urn": "urn:li:tag:dc_display_in_catalogue",
                                                "properties": {
                                                    "name": "dc_display_in_catalogue"
                                                },
                                            }
                                        }
                                    ]
                                },
                            },
                        }
                    ],
                },
                "name": "Dataset",
                "properties": {
                    "name": "Dataset",
                    "qualifiedName": "Foo.Dataset",
                    "description": "Dataset",
                    "customProperties": [
                        {"key": "sensitivityLevel", "value": "OFFICIAL"}
                    ],
                    "lastModified": {"time": 1709619407814},
                },
                "editableProperties": None,
                "tags": {
                    "tags": [
                        {
                            "tag": {
                                "urn": "urn:li:tag:Entity",
                                "properties": {"name": "some-tag"},
                            }
                        }
                    ]
                },
                "lastIngested": 1709619407814,
                "domain": None,
                "provider": "LAA",
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
                    ],
                    "primaryKeys": ["urn"],
                    "foreignKeys": [
                        {
                            "name": "DownstreamOf",
                            "foreignFields": [{"fieldPath": "urn"}],
                            "foreignDataset": {
                                "urn": "urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)",
                                "properties": {
                                    "name": "Dataset",
                                    "qualifiedName": None,
                                },
                            },
                            "sourceFields": [{"fieldPath": "urn"}],
                        },
                    ],
                },
            }
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)
        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            dataset = datahub_client.get_table_details(urn)

        assert dataset == Table(
            urn="abc",
            display_name="Dataset",
            name="Dataset",
            fully_qualified_name="Foo.Dataset",
            description="Dataset",
            relationships={
                RelationshipType.DATA_LINEAGE: [],
                RelationshipType.PARENT: [
                    EntitySummary(
                        entity_ref=EntityRef(
                            urn="urn:li:container:database", display_name="database"
                        ),
                        description="",
                        tags=[
                            TagRef(
                                urn="urn:li:tag:dc_display_in_catalogue",
                                display_name="dc_display_in_catalogue",
                            )
                        ],
                        entity_type="Database",
                    )
                ],
            },
            domain=DomainRef(display_name="", urn=""),
            governance=Governance(
                data_owner=OwnerRef(display_name="", email="", urn=""),
                data_stewards=[],
            ),
            tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
            metadata_last_ingested=1709619407814,
            data_last_modified=1709619407814,
            provider="LAA",
            created=None,
            platform=EntityRef(urn="datahub", display_name="datahub"),
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
                )
            ],
        )

    def test_get_dataset_minimal_properties(
        self,
        datahub_client,
        base_mock_graph,
    ):
        urn = "abc"
        datahub_response = {
            "dataset": {
                "platform": {"name": "datahub"},
                "name": "notinproperties",
                "properties": {},
                "downstream_lineage_relations": {"total": 0, "relationships": []},
                "upstream_lineage_relations": {"total": 0, "relationships": []},
                "parent_container_relations": {"total": 0, "relationships": []},
                "data_product_relations": {"total": 0, "relationships": []},
                "schemaMetadata": {"fields": []},
            }
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            dataset = datahub_client.get_table_details(urn)

        assert dataset == Table(
            urn="abc",
            display_name="notinproperties",
            name="notinproperties",
            fully_qualified_name="notinproperties",
            description="",
            relationships={
                RelationshipType.PARENT: [],
                RelationshipType.DATA_LINEAGE: [],
            },
            domain=DomainRef(display_name="", urn=""),
            governance=Governance(
                data_owner=OwnerRef(display_name="", email="", urn=""),
                data_stewards=[],
            ),
            tags=[],
            metadata_last_ingested=None,
            created=None,
            platform=EntityRef(urn="datahub", display_name="datahub"),
            custom_properties=CustomEntityProperties(
                usage_restrictions=UsageRestrictions(
                    dpia_required=None,
                    dpia_location="",
                ),
                access_information=AccessInformation(
                    dc_where_to_access_dataset="",
                    source_dataset_name="",
                    s3_location="",
                ),
                data_summary=DataSummary(),
                further_information=FurtherInformation(),
                audience=Audience.INTERNAL,
            ),
            column_details=[],
        )

    def test_get_chart_details(self, datahub_client, base_mock_graph):
        urn = "urn:li:chart:(justice-data,absconds)"
        datahub_response = {
            "chart": {
                "urn": "urn:li:chart:(justice-data,absconds)",
                "type": "CHART",
                "platform": {"name": "justice-data"},
                "relationships": {"total": 0, "relationships": []},
                "ownership": None,
                "properties": {
                    "name": "Absconds",
                    "externalUrl": "https://data.justice.gov.uk/prisons/public-protection/absconds",
                    "description": "a test description",
                    "customProperties": [],
                    "lastModified": {"time": 0},
                },
            },
            "extensions": {},
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            chart = datahub_client.get_chart_details(urn)

        assert chart == Chart(
            urn="urn:li:chart:(justice-data,absconds)",
            display_name="Absconds",
            name="Absconds",
            fully_qualified_name="Absconds",
            description="a test description",
            relationships={RelationshipType.PARENT: []},
            domain=DomainRef(display_name="", urn=""),
            governance=Governance(
                data_owner=OwnerRef(display_name="", email="", urn=""),
                data_stewards=[],
            ),
            tags=[],
            metadata_last_ingested=None,
            created=None,
            platform=EntityRef(urn="justice-data", display_name="justice-data"),
            custom_properties=CustomEntityProperties(
                usage_restrictions=UsageRestrictions(
                    dpia_required=None,
                    dpia_location="",
                ),
                access_information=AccessInformation(
                    dc_where_to_access_dataset="",
                    source_dataset_name="",
                    s3_location="",
                ),
                data_summary=DataSummary(),
                further_information=FurtherInformation(),
                audience=Audience.INTERNAL,
            ),
            external_url="https://data.justice.gov.uk/prisons/public-protection/absconds",
        )

    def test_get_publication_collection_details(self, datahub_client, base_mock_graph):
        urn = "urn:li:container:some_publication"
        datahub_response = {
            "container": {
                "urn": "urn:li:container",
                "type": "CONTAINER",
                "platform": {"name": "platform"},
                "properties": {
                    "name": "some publication",
                },
                "parentContainers": {
                    "count": 0,
                },
                "relationships": {
                    "total": 1,
                    "relationships": [
                        {
                            "entity": {
                                "name": "publication",
                                "urn": "urn:li:dataset:publication",
                                "properties": {"name": "publication"},
                                "tags": {
                                    "tags": [
                                        {
                                            "tag": {
                                                "urn": "urn:li:tag:dc_display_in_catalogue",
                                                "properties": {
                                                    "name": "dc:display_in_catalogue",
                                                },
                                            }
                                        }
                                    ]
                                },
                            }
                        }
                    ],
                },
            }
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            collection = datahub_client.get_publication_collection_details(urn)

        expected_relationships = {
            RelationshipType.CHILD: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:dataset:publication", display_name="publication"
                    ),
                    description="",
                    entity_type="publication_dataset",
                    tags=[
                        TagRef(
                            display_name="dc:display_in_catalogue",
                            urn="urn:li:tag:dc_display_in_catalogue",
                        )
                    ],
                )
            ]
        }

        expected_custom_properties = CustomEntityProperties(
            usage_restrictions=UsageRestrictions(dpia_required=None, dpia_location=""),
            access_information=AccessInformation(
                dc_where_to_access_dataset="",
                source_dataset_name="",
                s3_location="",
                dc_access_requirements="",
            ),
            data_summary=DataSummary(row_count="", refresh_period=""),
            further_information=FurtherInformation(
                dc_slack_channel_name="",
                dc_slack_channel_url="",
                dc_teams_channel_name="",
                dc_teams_channel_url="",
                dc_team_email="",
            ),
            audience="Internal",
        )

        expected = PublicationCollection(
            urn="urn:li:container:some_publication",
            display_name="some publication",
            name="some publication",
            fully_qualified_name="some publication",
            description="",
            relationships=expected_relationships,
            domain=DomainRef(display_name="", urn=""),
            governance=Governance(
                data_owner=OwnerRef(display_name="", email="", urn=""),
                data_stewards=[],
                data_custodians=[],
            ),
            tags=[],
            glossary_terms=[],
            metadata_last_ingested=None,
            created=None,
            data_last_modified=None,
            platform=EntityRef(urn="platform", display_name="platform"),
            custom_properties=expected_custom_properties,
            external_url="",
        )

        assert collection == expected

    def test_get_database_details_filters_entities(
        self, datahub_client, base_mock_graph
    ):
        urn = "urn:li:container:foo"
        datahub_response = {
            "container": {
                "urn": "urn:li:container",
                "type": "CONTAINER",
                "platform": {"name": "platform"},
                "parentContainers": {
                    "count": 0,
                },
                "relationships": {
                    "total": 2,
                    "relationships": [
                        {
                            "entity": {
                                "name": "DatasetToShow",
                                "urn": "urn:li:dataset:DatasetToShow",
                                "properties": {
                                    "name": "DatasetToShow",
                                    "description": "Dataset to show",
                                },
                                "tags": {
                                    "tags": [
                                        {
                                            "tag": {
                                                "urn": "urn:li:tag:dc_display_in_catalogue",
                                                "properties": {
                                                    "name": "dc:display_in_catalogue",
                                                },
                                            }
                                        }
                                    ]
                                },
                            }
                        },
                        {
                            "entity": {
                                "name": "DatasetToHide",
                                "urn": "urn:li:dataset:DatasetToHide",
                                "properties": {
                                    "name": "DatasetToHide",
                                    "description": "Dataset to hide",
                                },
                                "tags": {"tags": []},
                            }
                        },
                    ],
                },
                "ownership": None,
                "properties": {
                    "name": "Some database",
                    "description": "a test description",
                    "customProperties": [],
                    "lastModified": {"time": 0},
                },
            },
            "extensions": {},
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            database = datahub_client.get_database_details(urn)
            assert database.relationships[RelationshipType.CHILD] == [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:dataset:DatasetToShow", display_name="DatasetToShow"
                    ),
                    description="Dataset to show",
                    entity_type="TABLE",
                    tags=[
                        TagRef(
                            urn="urn:li:tag:dc_display_in_catalogue",
                            display_name="dc:display_in_catalogue",
                        )
                    ],
                )
            ]

    def test_upsert_table_and_database(
        self,
        datahub_client,
        base_mock_graph,
        database,
        table,
        tmp_path,
        check_snapshot,
        golden_file_in_db,
    ):
        """
        Case where we create separate database and table
        """
        base_mock_graph.import_file(golden_file_in_db)
        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            fqn_db = datahub_client.upsert_database(database=database)
            fqn_t = datahub_client.upsert_table(table=table)

        fqn_db_out = "urn:li:container:my_database"
        assert fqn_db == fqn_db_out

        fqn_t_out = "urn:li:dataset:(urn:li:dataPlatform:athena,database.Dataset,PROD)"
        assert fqn_t == fqn_t_out

        output_file = Path(tmp_path / "test_upsert_table_and_database.json")
        base_mock_graph.sink_to_file(output_file)
        check_snapshot("test_upsert_table_and_database.json", output_file)

    def test_upsert_table(
        self,
        datahub_client,
        table,
        base_mock_graph,
        tmp_path,
        check_snapshot,
        golden_file_in_db,
    ):
        """
        Case where we create a dataset via upsert_table method
        """
        mock_graph = base_mock_graph
        mock_graph.import_file(golden_file_in_db)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            fqn = datahub_client.upsert_table(
                table=table,
            )
        fqn_out = "urn:li:dataset:(urn:li:dataPlatform:athena,database.Dataset,PROD)"

        assert fqn == fqn_out

        output_file = Path(tmp_path / "test_upsert_table.json")
        base_mock_graph.sink_to_file(output_file)
        check_snapshot("test_upsert_table.json", output_file)

    def test_domain_does_not_exist_error(self, datahub_client, database):
        with pytest.raises(InvalidDomain):
            datahub_client.upsert_database(database=database)

    def test_database_not_exist_given_error(self, datahub_client, table, database):
        with pytest.raises(ReferencedEntityMissing):
            datahub_client.upsert_table(table=table)

    def test_get_custom_property_key_value_pairs(self, datahub_client, database):
        datahub_client._get_custom_property_key_value_pairs(database.custom_properties)

    def test_get_dataset_invalid_urn(self, datahub_client, base_mock_graph):
        urn = "invalid_urn"
        datahub_response = {"dataset": None}
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = False  # Entity does not exist
            with pytest.raises(EntityDoesNotExist):
                datahub_client.get_table_details(urn)

    def test_get_dataset_missing_properties(self, datahub_client, base_mock_graph):
        urn = "urn:li:dataset:missing_props"
        datahub_response = {
            "dataset": {
                "platform": {"name": "datahub"},
                "name": "Dataset",
                "properties": {},
            }
        }
        base_mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

        with patch(
            "data_platform_catalogue.client.datahub_client.DataHubCatalogueClient.check_entity_exists_by_urn"
        ) as mock_exists:
            mock_exists.return_value = True
            dataset = datahub_client.get_table_details(urn)

        assert dataset.name == "Dataset"
        assert dataset.description == ""
