from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import AfterValidator, BaseModel, EmailStr, Field
from typing_extensions import Annotated

from .validators import check_timestamp_is_in_the_past

DATAHUB_DATE_FORMAT = "%Y%m%d"


class RelationshipType(Enum):
    PARENT = "PARENT"
    PLATFORM = "PLATFORM"
    DATA_LINEAGE = "DATA_LINEAGE"
    CHILD = "CHILD"


class DatahubEntityType(Enum):
    CONTAINER = "CONTAINER"
    DATASET = "DATASET"
    DASHBOARD = "DASHBOARD"
    CHART = "CHART"
    GLOSSARY_TERM = "GLOSSARY_TERM"


class DatahubSubtype(Enum):
    PUBLICATION_DATASET = "Publication dataset"
    PUBLICATION_COLLECTION = "Publication collection"
    METRIC = "Metric"
    TABLE = "Table"
    MODEL = "Model"
    SEED = "Seed"
    SOURCE = "Source"
    DATABASE = "Database"


class FindMoJdataEntityType(Enum):
    TABLE = "Table"
    GLOSSARY_TERM = "Glossary term"
    CHART = "Chart"
    DATABASE = "Database"
    DASHBOARD = "Dashboard"
    PUBLICATION_DATASET = "Publication dataset"
    PUBLICATION_COLLECTION = "Publication collection"


@dataclass
class FindMoJdataEntityMapper:
    find_moj_data_type: FindMoJdataEntityType
    datahub_type: DatahubEntityType
    datahub_subtypes: list[str]
    url_formatted: str


TableEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.TABLE,
    DatahubEntityType.DATASET,
    [
        DatahubSubtype.MODEL.value,
        DatahubSubtype.TABLE.value,
        DatahubSubtype.SEED.value,
        DatahubSubtype.SOURCE.value,
    ],
    "table",
)

ChartEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.CHART, DatahubEntityType.CHART, [], "chart"
)

GlossaryTermEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.GLOSSARY_TERM,
    DatahubEntityType.GLOSSARY_TERM,
    [],
    "glossary_term",
)

DatabaseEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.DATABASE,
    DatahubEntityType.CONTAINER,
    [DatahubSubtype.DATABASE.value],
    "database",
)

DashboardEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.DASHBOARD, DatahubEntityType.DASHBOARD, [], "dashboard"
)

PublicationDatasetEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.PUBLICATION_DATASET,
    DatahubEntityType.DATASET,
    [DatahubSubtype.PUBLICATION_DATASET.value],
    "publication_dataset",
)

PublicationCollectionEntityMapping = FindMoJdataEntityMapper(
    FindMoJdataEntityType.PUBLICATION_COLLECTION,
    DatahubEntityType.CONTAINER,
    [DatahubSubtype.PUBLICATION_COLLECTION.value],
    "publication_collection",
)

Mappers = [
    TableEntityMapping,
    ChartEntityMapping,
    GlossaryTermEntityMapping,
    DatabaseEntityMapping,
    DashboardEntityMapping,
    PublicationDatasetEntityMapping,
    PublicationCollectionEntityMapping,
]


class Classification(Enum):
    """Enumeration representing the security classification of the data.
    Attributes:
        OFFICIAL (str): Represents data classified as "Official".
        OFFICIAL_SENSITIVE (str): Represents data classified as "Official-Sensitive".
    Notes:
        This enumeration replaces the Audience entity.
        - "Published" becomes "Official".
        - "Internal" becomes "Official-Sensitive".
    """

    OFFICIAL = "Official"
    OFFICIAL_SENSITIVE = "Official-Sensitive"


class EntityRef(BaseModel):
    """
    A reference to another entity in the metadata graph.
    """

    urn: str = Field(
        description="The identifier of the entity being linked to.",
        examples=[
            "urn:li:chart:(justice-data,absconds)",
            "urn:li:glossaryTerm:f045591e-182a-45fd-9b06-ebbc222606d6",
        ],
    )
    display_name: str = Field(
        description="Display name that can be used for link text.",
        examples=["absconds", "Common platform"],
    )


class ColumnRef(BaseModel):
    """
    A reference to a column in a table
    """

    name: str = Field(
        description=(
            "The column name or dotted path that identifies the column within the "
            "schema. This uses Datahub's FieldPath encoding scheme, and may include "
            "type and versioning information."
        ),
        examples=["custody_id", "table_name.custody_id"],
    )
    display_name: str = Field(
        description="A user-friendly version of the name", examples=["custody_id"]
    )
    table: EntityRef = Field(
        description="Reference to the table the column belongs to",
        examples=[
            EntityRef(
                urn="urn:li:dataset:(urn:li:dataPlatform:dbt,delius.custody_dates,PROD)",
                display_name="delius.custody_dates",
            )
        ],
    )


class Column(BaseModel):
    """
    A column definition in a table
    """

    name: str = Field(
        description=(
            "The column name or dotted path that identifies the column within the "
            "schema. This uses Datahub's FieldPath encoding scheme, and may include "
            "type and versioning information."
        ),
        examples=["parole_elibility_date", "table_name.custody_id"],
    )
    display_name: str = Field(
        description="A user-friendly version of the name",
        examples=["parole_elibility_date"],
    )
    type: str = Field(
        description="The data type of the column as it appears in the table",
        examples=["timestamp", "int"],
    )
    description: str = Field(
        description="A description of the column",
        examples=["Unique identifier for custody event"],
    )
    nullable: bool = Field(
        description="Whether the field is nullable or not", examples=[True, False]
    )
    is_primary_key: bool = Field(
        description="Whether the field is part of the primary key",
        examples=[True, False],
    )
    foreign_keys: list[ColumnRef] = Field(
        description="References to columns in other tables", default_factory=list
    )


class OwnerRef(BaseModel):
    """
    A reference to a named individual that performs some kind of governance
    """

    display_name: str = Field(
        description="The full name of the user as it should be displayed",
        examples=["John Doe", "Jane Smith"],
    )
    email: EmailStr | Literal[""] = Field(
        description="Contact email for the user", examples=["john.doe@justice.gov.uk"]
    )
    urn: str = Field(
        description="Unique identifier for the user",
        examples=["urn:li:corpuser:jane.smith"],
    )


class Governance(BaseModel):
    """
    Governance model for an entity or domain
    """

    data_owner: OwnerRef = Field(
        description="Senior leader within the business (DD and above) who sponsors and champions data governance work within their data domain.",  # noqa: E501
        examples=[
            OwnerRef(
                display_name="John Doe",
                email="jogn.doe@justice.gov.uk",
                urn="urn:li:corpuser:john.doe",
            )
        ],
    )
    data_stewards: list[OwnerRef] = Field(
        description="Subject matter expert within a business area (SEO – DD) or the associated data domain, acting as a go-between for business users and digital teams/system owners.",  # noqa: E501
        examples=[
            [
                OwnerRef(
                    display_name="Jane Smith",
                    email="jane.smith@justice.gov.uk",
                    urn="urn:li:corpuser:jane.smith",
                )
            ]
        ],
        default_factory=list,
    )
    data_custodians: list[OwnerRef] = Field(
        description="Responsible for the capture, storage, and disposal of data as per the Data owner and Data steward’s requirements, and within the limits of data quality and security limitations.",  # noqa: E501
        examples=[
            [
                OwnerRef(
                    display_name="Rosanne Columns",
                    email="rosanne.columns@justice.gov.uk",
                    urn="urn:li:corpuser:rosanne.columns",
                )
            ]
        ],
        default_factory=list,
    )


class TagRef(BaseModel):
    """
    Reference to a tag
    """

    @classmethod
    def from_name(cls, name):
        return cls(display_name=name, urn=f"urn:li:tag:{name}")

    display_name: str = Field(
        description="Human friendly tag name",
        examples=["PII"],
    )
    urn: str = Field(
        description="The identifier of the tag",
        examples=["urn:li:tag:PII"],
    )


class GlossaryTermRef(BaseModel):
    """
    Reference to a Glossary term
    """

    display_name: str = Field(
        description="Glossary term name",
        examples=["PII"],
    )
    urn: str = Field(
        description="The identifier of the glossary term",
        examples=["urn:li:glossaryTerm:ESDA"],
    )
    description: str = Field(
        description="The definition of the glossary term",
        examples=["Essential Shared Data Asset"],
    )


class UsageRestrictions(BaseModel):
    """
    Metadata about how entities may be used.
    """

    dpia_required: bool | None = Field(
        description=(
            "Bool for if a data privacy impact assessment (DPIA) is required to access "
            "this database"
        ),
        default=None,
        examples=[True, False],
    )
    dpia_location: str = Field(
        description="Where to find the DPIA document", default="", examples=["OneTrust"]
    )


class AccessInformation(BaseModel):
    """
    Any metadata about how to access a data entity.
    The same data entity may be accessable via multiple means.
    """

    dc_where_to_access_dataset: str = Field(
        description="Descriptor for where the data can be accessed.",
        default="",
        examples=["analytical_platform"],
    )
    source_dataset_name: str = Field(
        description="The name of a dataset this data was derived from",
        default="",
        examples=["stg_xhibit_bw_history"],
    )
    s3_location: str = Field(
        description="Location of the data in s3",
        default="",
        examples=[
            "s3://calculate-release-dates/data/database_name=dbf2e4/table_name=approved_dates/",  # noqa: E501
            "s3://alpha-hmpps-reports-data",
        ],
    )
    dc_access_requirements: str = Field(
        description="Paragraph explaning whether there are any specific access requirements related these data.",
        default="",
        examples=[
            "Processing of these data requires a DPIA",
        ],
    )


class EntitySummary(BaseModel):
    """
    EntitySummary can be used to hold information for entities that is required to be displayed on
    details pages
    """

    entity_ref: EntityRef = Field(
        description="The entity reference containing name and urn"
    )
    description: str = Field(description="A description of the entity")
    entity_type: str = Field(
        description="indicates the type of entity that is summarised"
    )
    tags: list[TagRef] = Field(description="Any tags associated with the entity")


class FurtherInformation(BaseModel):
    """
    Routes to further information about the data.
    E.g. external links to docs, reference materials, knowledge sites, discussion forums.
    """

    dc_slack_channel_name: str = Field(
        description=(
            "The name of a slack channel to be used as a contact point for users of "
            "the catalogue service, including the leading '#'. Note: this is not the "
            "same as the owner channel for notifications."
        ),
        default="",
        examples=["#data-engineering"],
    )
    dc_slack_channel_url: str = Field(
        description="The URL to the slack channel",
        default="",
        examples=["https://moj.enterprise.slack.com/archives/CXYZ1234E"],
    )
    dc_teams_channel_name: str = Field(
        description=(
            "The name of a Microsoft Teams channel to be used as a contact point for users of "
            "the catalogue service to ask questions."
        ),
        default="",
        examples=["Data team"],
    )
    dc_teams_channel_url: str = Field(
        description="The URL to the Teams channel",
        default="",
        examples=["https://teams.microsoft.com/l/channel/123"],
    )
    dc_team_email: EmailStr | Literal[""] = Field(
        description=(
            "A shared email address for a team where they receive questions"
            " about the data. Unrealted to Microsoft Teams"
        ),
        default="",
        examples=["best-data-team@justice.gov.uk"],
    )


class DataSummary(BaseModel):
    """
    Summarised information derived from the actual data.
    """

    row_count: int | str = Field(
        description="Row count when the metadata was last updated",
        default="",
        examples=["123", 123],
    )
    refresh_period: str = Field(
        description="Indicates the frequency that the data are refreshed/updated",
        default="",
        examples=["Annually", "Quarterly", "Monthly", "Weekly", "Daily"],
    )


class CustomEntityProperties(BaseModel):
    """Custom entity properties not part of DataHub's entity model"""

    usage_restrictions: UsageRestrictions = Field(
        description="Limitations on how the data may be used and accessed",
        default_factory=UsageRestrictions,
    )
    access_information: AccessInformation = Field(
        description="Metadata about how to access a data entity",
        default_factory=AccessInformation,
    )
    data_summary: DataSummary = Field(
        description="Summary of data stored in this table", default_factory=DataSummary
    )
    further_information: FurtherInformation = Field(
        description="Routes to further information about the data",
        default_factory=FurtherInformation,
    )
    classification: Classification = Field(
        description="If the data is published or not",
        default="Official-Sensitive",
    )

    class Config:
        use_enum_values = True


class Entity(BaseModel):
    """
    Any searchable data entity that is present in the metadata graph, which
    may be related to other entities.
    Examples include platforms, databases, tables
    """

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:tag:PII", "urn:li:chart:(justice-data,absconds)"],
    )
    display_name: str | None = Field(
        description="Display name of the entity", examples=["Absconds"]
    )
    name: str = Field(
        description="Actual name of the entity in its source platform",
        examples=["Absconds"],
    )
    fully_qualified_name: str | None = Field(
        description="Fully qualified name of the entity in its source platform",
        examples=["database.absconds", "Absconds"],
    )
    description: str = Field(
        description=(
            "Detailed description about what functional area this entity is "
            "representing, what purpose it has and business related information."
        ),
        examples=[
            (
                "This entity has one row for each sentence in a court. Note that only"
                "the primary sentence is recorded rather than the secondary sentence."
            )
        ],
    )
    relationships: dict[RelationshipType, list[EntitySummary]] = Field(
        default={},
        description=(
            "References to related entities in the metadata graph, such as platform or "
            "parent entities"
        ),
        examples=[
            {
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
            }
        ],
    )
    subject_areas: list[TagRef] = Field(
        description="The subject areas this entity belongs to",
        examples=[TagRef(display_name="Prisons", urn="urn:li:tag:Prisons")],
    )
    governance: Governance = Field(description="Information about governance")
    tags: list[TagRef] = Field(
        default_factory=list,
        description="Additional tags to add.",
        examples=[[TagRef(display_name="ESDA", urn="urn:li:tag:ESDA")]],
    )
    glossary_terms: list[GlossaryTermRef] = Field(
        default_factory=list,
        description="Glossary Terms the entity relates to.",
        examples=[
            [
                GlossaryTermRef(
                    display_name="Essential Shared Data Asset (ESDA)",
                    urn="urn:li:glossaryTerm:ESDA",
                    description="An ESDA is...",
                )
            ]
        ],
    )
    metadata_last_ingested: Annotated[
        Optional[datetime], AfterValidator(check_timestamp_is_in_the_past)
    ] = Field(
        description="When the metadata was last updated in the catalogue",
        default=None,
        examples=[datetime(2011, 10, 2, 3, 0, 0)],
    )
    created: Annotated[
        Optional[datetime], AfterValidator(check_timestamp_is_in_the_past)
    ] = Field(
        description="When the data entity was first created",
        default=None,
        examples=[datetime(2011, 10, 2, 3, 0, 0)],
    )
    data_last_modified: Annotated[
        Optional[datetime], AfterValidator(check_timestamp_is_in_the_past)
    ] = Field(
        description="When the data entity was last modified in the source system",
        default=None,
        examples=[datetime(2011, 10, 2, 3, 0, 0)],
    )
    platform: EntityRef = Field(
        description=(
            "The platform that an entity should belong to, e.g. Glue, Athena, DBT. "
            "Should exist in datahub"
        ),
        examples=[EntityRef(urn="urn:li:dataPlatform:kafka", display_name="Kafka")],
    )
    custom_properties: CustomEntityProperties = Field(
        description="Fields to add to DataHub custom properties",
        default_factory=CustomEntityProperties,
    )
    tags_to_display: list[str] = Field(
        description="a list of tag display_names where tags starting 'dc_' are filtered out",  # noqa: E501
        init=False,
        default=[],
    )

    def model_post_init(self, __context):
        self.tags_to_display = [
            tag.display_name
            for tag in self.tags
            if not tag.display_name.startswith("dc_")
        ]


class Database(Entity):
    """For source system databases"""

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:container:my_database"],
    )


class PublicationCollection(Entity):
    """For source system publication collections"""

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:container:criminal_justice_stats"],
    )
    external_url: str = Field(
        description="URL to view the collection",
        examples=["https://data.justice.gov.uk/prisons/criminal-jsutice/publications"],
    )


class PublicationDataset(Entity):
    """For source system publication collections"""

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:dataset:(urn:li:dataPlatform:gov.uk,statistics2011,DEV)"],
    )
    external_url: str = Field(
        description="URL to view the collection",
        examples=["https://data.justice.gov.uk/prisons/criminal-jsutice/publications"],
    )


class Table(Entity):
    """A table in a database or a tabular dataset. DataHub calls them datasets."""

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:dataset:(urn:li:dataPlatform:redshift,public.table,DEV)"],
    )

    subtypes: list[str] = Field(
        description=(
            "List of datahub subtypes. If a subtype is set, we still model the entity "
            "as a table in Find MoJ data."
        ),
        examples=[["Metric"]],
        default=[],
    )
    column_details: list[Column] = Field(
        description=(
            "A list of objects which relate to columns in your data, each list item "
            "will contain, a name of the column, data type of the column and "
            "description of the column."
        ),
        examples=[
            [
                Column(
                    name="custody_id",
                    display_name="custody_id",
                    type="int",
                    description="unique ID for custody",
                    nullable=False,
                    is_primary_key=True,
                ),
            ]
        ],
    )
    last_datajob_run_date: Annotated[
        Optional[datetime], AfterValidator(check_timestamp_is_in_the_past)
    ] = Field(
        description="Indicates the time when the data were last refreshed (eg pipeline run with dbt).",
        default=None,
        examples=[datetime(2011, 10, 2, 3, 0, 0)],
    )


class Chart(Entity):
    """A visualisation of a dataset"""

    urn: str | None = Field(
        description="Unique identifier for the entity. Relates to Datahub's urn",
        examples=["urn:li:chart:(justice-data,absconds)"],
    )
    external_url: str = Field(
        description="URL to view the chart",
        examples=["https://data.justice.gov.uk/prisons/public-protection/absconds"],
    )


class Dashboard(Entity):
    external_url: str = Field(
        description="URL to view the dashboard",
        examples=["https://data.justice.gov.uk"],
    )


class SubjectAreaTaxonomy:
    ALL_SUBJECT_AREAS = [
        TagRef.from_name("Bold"),
        TagRef.from_name("Civil"),
        TagRef.from_name("Courts"),
        TagRef.from_name("Electronic monitoring"),
        TagRef.from_name("Finance"),
        TagRef.from_name("General"),
        TagRef.from_name("Interventions"),
        TagRef.from_name("OPG"),
        TagRef.from_name("People"),
        TagRef.from_name("Prison"),
        TagRef.from_name("Probation"),
        TagRef.from_name("Property"),
        TagRef.from_name("Risk"),
    ]

    @classmethod
    def get_by_name(cls, name):
        matches = [i for i in cls.ALL_SUBJECT_AREAS if i.display_name == name]
        return matches[0] if matches else None

    @classmethod
    def is_subject_area(cls, name):
        return cls.get_by_name(name) is not None
