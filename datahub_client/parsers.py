import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Tuple

from datahub_client.entities import (
    AccessInformation,
    Chart,
    ChartEntityMapping,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Dashboard,
    DashboardEntityMapping,
    Database,
    DatabaseEntityMapping,
    DatahubEntityType,
    DatahubSubtype,
    DataSummary,
    Entity,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    GlossaryTermEntityMapping,
    GlossaryTermRef,
    Governance,
    OwnerRef,
    PublicationCollection,
    PublicationCollectionEntityMapping,
    PublicationDataset,
    PublicationDatasetEntityMapping,
    RelationshipType,
    SubjectAreaTaxonomy,
    Table,
    TableEntityMapping,
    TagRef,
    UsageRestrictions,
)
from datahub_client.search.search_types import SearchResult

logger = logging.getLogger(__name__)

PROPERTIES_EMPTY_STRING_FIELDS = ("description", "externalUrl")
DATA_OWNER = "urn:li:ownershipType:__system__dataowner"
DATA_STEWARD = "urn:li:ownershipType:__system__data_steward"
DATA_CUSTODIAN = "urn:li:ownershipType:data_custodian"


class EntityParser:

    def parse(self, search_response) -> SearchResult:
        """Parse graphql response to a SearchResult object"""
        raise NotImplementedError

    def parse_to_entity_object(self, response: dict, urn: str) -> Entity:
        """Parse graphql response to an Entity object"""
        raise NotImplementedError

    @staticmethod
    def parse_names(
        entity: dict[str, Any], properties: dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Returns a tuple of 3 name values.

        The first value is the non-qualified version of the entity name,
        and the second value is the human-friendly display name.

        Either of these can be used when showing the entity providing it is within
        the context of its container.

        The third value is the fully qualified name (e.g. my_database.my_table), which
        can be used to show the entity out of context.
        """
        top_level_name = entity.get("name", "")
        name = properties.get("name", top_level_name)
        display_name = properties.get("displayName") or name
        qualified_name = properties.get("qualifiedName") or top_level_name or name

        return name, display_name, qualified_name

    @staticmethod
    def parse_name(entity: dict[str, Any]) -> str:
        """
        Parse the name of an entity, falling back to
        the legacy field if unavailable.
        """
        properties = entity.get("properties") or {}
        return properties.get("name") or entity.get("name", "")

    @staticmethod
    def parse_description(entity: dict[str, Any]) -> str:
        properties = entity.get("properties") or {}
        return properties.get("description") or ""

    @staticmethod
    def parse_tags(entity: dict[str, Any]) -> list[TagRef]:
        """
        Parse tag information into a list of TagRef objects for displaying
        as part of the search result.
        """
        outer_tags = entity.get("tags") or {}
        tags = []
        for tag in outer_tags.get("tags", []):
            properties = tag.get("tag", {}).get("properties", {})
            # This is needed because tags created by dbt seemingly don't have properties
            # populated
            if not properties and tag.get("tag", {}).get("urn"):
                properties = {
                    "name": tag.get("tag", {}).get("urn").replace("urn:li:tag:", "")
                }

            name = properties.get("name", "")
            if properties and not SubjectAreaTaxonomy.is_subject_area(name):
                tags.append(
                    TagRef(
                        display_name=name,
                        urn=tag.get("tag", {}).get("urn", ""),
                    )
                )
        return tags

    def parse_subject_areas(self, entity: dict[str, Any]) -> list[TagRef]:
        result = []
        outer_tags = entity.get("tags") or {}
        for tag in outer_tags.get("tags", []):
            tag_inner = tag["tag"]
            properties = tag.get("properties") or {}
            name = properties.get("name") or tag_inner.get("name")

            subject_area = SubjectAreaTaxonomy.get_by_name(name)
            if subject_area is None:
                continue
            else:
                result.append(TagRef(display_name=name, urn=subject_area.urn))

        return result

    @staticmethod
    def get_refresh_period_from_cadet_tags(
        tags: list[TagRef],
        refresh_schedules: tuple[str] = ("daily", "weekly", "monthly"),
    ) -> str:
        # Check if any of the tags are refresh period tags eg "daily_opg"
        relevant_refresh_schedules = [
            schedule
            for tag_ref in tags
            for schedule in refresh_schedules
            if schedule in tag_ref.display_name
        ]
        if len(relevant_refresh_schedules) > 1:
            logger.warning(f"More than one refresh period tag found: {tags=}")

        if relevant_refresh_schedules:
            refresh_schedule = ", ".join(relevant_refresh_schedules).capitalize()
            return refresh_schedule

        return ""

    def parse_properties(
        self, entity: dict[str, Any]
    ) -> Tuple[dict[str, Any], CustomEntityProperties]:
        """
        Parse properties and editableProperties into a single dictionary.
        """
        properties = entity["properties"] or {}
        editable_properties = entity.get("editableProperties") or {}
        properties.update(editable_properties)

        for key in PROPERTIES_EMPTY_STRING_FIELDS:
            try:
                properties[key] = properties[key] or ""
            except KeyError:
                pass

        custom_properties_dict = {
            i["key"]: i["value"] or "" for i in properties.get("customProperties", [])
        }

        if "dpia_required" in custom_properties_dict:
            custom_properties_dict["dpia_required"] = (
                custom_properties_dict["dpia_required"] == "True"
            )

        properties.pop("customProperties", None)
        access_information = AccessInformation.model_validate(custom_properties_dict)
        usage_restrictions = UsageRestrictions.model_validate(custom_properties_dict)
        data_summary = DataSummary.model_validate(custom_properties_dict)

        tags = self.parse_tags(entity)
        cadet_refresh_period = self.get_refresh_period_from_cadet_tags(tags)
        if cadet_refresh_period:
            data_summary.refresh_period = cadet_refresh_period
        audience = custom_properties_dict.get("audience", "Internal")

        further_information = FurtherInformation.model_validate(custom_properties_dict)

        custom_properties = CustomEntityProperties(
            access_information=access_information,
            usage_restrictions=usage_restrictions,
            data_summary=data_summary,
            further_information=further_information,
            audience=audience,
        )

        return properties, custom_properties

    def parse_data_owner(self, entity: dict[str, Any]) -> OwnerRef:
        """
        Parse ownership information, if it is set, and return the first owner of
        type `ownership_type_urn`.
        If no owner information exists, return an OwnerRef populated with blank strings
        """
        ownership = entity.get("ownership") or {}
        owners = [
            i["owner"]
            for i in ownership.get("owners", [])
            if i["ownershipType"]["urn"] == DATA_OWNER
        ]

        if owners:
            return self._parse_owner_object(owners[0])
        else:
            return OwnerRef(display_name="", email="", urn="")

    @staticmethod
    def parse_glossary_terms(entity: dict[str, Any]) -> list[GlossaryTermRef]:
        """
        Parse glossary_term information into a list of TagRef for displaying
        as part of the search result.
        """
        outer_terms = entity.get("glossaryTerms") or {}
        terms = []
        for term in outer_terms.get("terms", []):
            properties = term.get("term", {}).get("properties", {})
            if properties:
                terms.append(
                    GlossaryTermRef(
                        display_name=properties.get("name", ""),
                        urn=term.get("term", {}).get("urn", ""),
                        description=properties.get("description", ""),
                    )
                )
        return terms

    @staticmethod
    def parse_data_last_modified(properties: dict[str, Any]) -> datetime | None:
        """
        Return the time when the data was last updated in the source system
        (not Datahub)
        """
        modified = (properties.get("lastModified") or {}).get("time")
        return None if modified == 0 else modified

    def _parse_owner_object(self, owner: dict) -> OwnerRef:
        properties = owner.get("properties") or {}
        display_name = (
            properties.get("displayName")
            if properties.get("displayName") is not None
            else properties.get("fullName", "")
        )
        return OwnerRef(
            display_name=display_name or "",
            email=properties.get(
                "email",
                self._make_user_email_from_urn(owner.get("urn")),
            ),
            urn=owner.get("urn", ""),
        )

    @staticmethod
    def _make_user_email_from_urn(urn) -> str:
        """
        Creates a user email using a user entity urn. This should only be called
        when an urn exists for a user that has not signed in to datahub via sso,
        so has not been created as an entity and has no associated email address.

        We will look to revist our approach to ownership user creation, see
        gitHub issue https://github.com/ministryofjustice/find-moj-data/issues/578,
        but for now this will fix the issue of owners being flagged in datahub but not
        showing in find-moj-data
        """
        username = urn.replace("urn:li:corpuser:", "")
        email = f"{username}@justice.gov.uk"
        return email

    @staticmethod
    def _get_matched_fields(result: dict) -> dict:
        fields = result.get("matchedFields", [])
        matched_fields = {}
        for field in fields:
            name = field.get("name")
            value = field.get("value")
            if name == "customProperties" and value != "":
                try:
                    name, value = value.split("=")
                except ValueError:
                    continue
            matched_fields[name] = value
        return matched_fields

    def parse_columns(self, entity: dict[str, Any]) -> list[Column]:
        """
        Parse the schema metadata from Datahub into a flattened list of column
        information.

        Note: The format of each column is similar to but not the same
        as the format used when ingesting table metadata.
        - `type` refers to the Datahub type, not AWS glue type
        - `nullable`, 'isPrimaryKey` and `foreignKeys` metadata is added
        """
        result = []

        schema_metadata = entity.get("schemaMetadata", {})
        if not schema_metadata:
            return []

        primary_keys = set(schema_metadata.get("primaryKeys") or ())

        foreign_keys = defaultdict(list)

        # Attempt to match foreign keys to the main fields.
        #
        # Assumptions:
        # - A given field may have multiple foreign keys to other datasets
        # - Some foreign keys will not match on fieldPath, because fields
        #   may be defined using STRUCT types and foreign keys can reference
        #   subfields within the struct. We will simply ignore these.
        for foreign_key in schema_metadata.get("foreignKeys") or ():
            if not foreign_key["sourceFields"] or not foreign_key["foreignFields"]:
                continue

            source_path = foreign_key["sourceFields"][0]["fieldPath"]
            foreign_path = foreign_key["foreignFields"][0]["fieldPath"]

            foreign_table = EntityRef(
                urn=foreign_key["foreignDataset"]["urn"],
                display_name=foreign_key["foreignDataset"]["properties"]["name"],
            )

            display_name = foreign_path.split(".")[-1]
            foreign_keys[source_path].append(
                ColumnRef(
                    name=foreign_path, display_name=display_name, table=foreign_table
                )
            )

        for field in schema_metadata.get("fields", ()):
            foreign_keys_for_field = foreign_keys[field["fieldPath"]]

            # Work out if the field is primary.
            # This is an oversimplification: in the case of a composite
            # primary key, we report that each component field is primary.
            is_primary_key = field["fieldPath"] in primary_keys
            field_path = field["fieldPath"]
            display_name = field_path.split(".")[-1]

            result.append(
                Column(
                    name=field_path,
                    display_name=display_name,
                    description=field.get("description") or "",
                    type=field.get("nativeDataType", field["type"]),
                    nullable=field["nullable"],
                    is_primary_key=is_primary_key,
                    foreign_keys=foreign_keys_for_field,
                )
            )

        # Sort primary keys first, then sort alphabetically
        return sorted(result, key=lambda c: (0 if c.is_primary_key else 1, c.name))

    def _parse_owners_by_type(
        self,
        entity: dict[str, Any],
        ownership_type_urn: str,
    ) -> list[OwnerRef]:
        """
        Parse ownership information, if it is set, and return a list of owners
        of type `ownership_type_urn`.
        If no owner information exists, the list will be empty.
        """
        ownership = entity.get("ownership") or {}
        owners = [
            i["owner"]
            for i in ownership.get("owners", [])
            if i["ownershipType"]["urn"] == ownership_type_urn
        ]

        return [self._parse_owner_object(owner) for owner in owners]

    def parse_stewards(self, entity: dict[str, Any]) -> list[OwnerRef]:
        """
        Parse ownership information, if it is set, and return a list of data stewards.
        If no owners exist with a matching ownership type, the list will be empty.
        """
        return self._parse_owners_by_type(entity, DATA_STEWARD)

    def parse_custodians(self, entity: dict[str, Any]) -> list[OwnerRef]:
        """
        Parse ownership information, if it is set, and return a list of data custodians.
        If no owners exist with a matching ownership type, the list will be empty.
        """
        return self._parse_owners_by_type(entity, DATA_CUSTODIAN)

    def parse_data_created(self, properties: dict[str, Any]) -> datetime | None:
        """
        Return the time when the data was created in the source system
        (not Datahub)
        """
        created = properties.get("created")
        return None if created == 0 else created

    def parse_relations(
        self,
        relationship_type: RelationshipType,
        relations_list: list[dict],
        relation_key="relationships",
        entity_type_of_relations: None | str = None,
    ) -> dict[RelationshipType, list[EntitySummary]]:
        """
        parse the relationships results returned from a graphql querys
        """

        # we may want to do something with total relations if we are returning child
        # relations and need to paginate through relations - 10 relations returned as is
        # There may be more than 10 lineage entities but since we currently only care
        # if lineage exists for a dataset we don't need to capture everything
        related_entities = []
        for all_relations in relations_list:
            for relation in all_relations.get(relation_key, []):
                urn = relation.get("entity").get("urn")
                # we sometimes have multiple sub-types loaded or no subtype
                if entity_type_of_relations is None:
                    entity_type = (
                        relation.get("entity")
                        .get("subTypes", {})
                        .get("typeNames", [relation.get("entity").get("type")])[0]
                        if relation.get("entity").get("subTypes") is not None
                        else [relation.get("entity").get("type")][0]
                    )
                else:
                    entity_type = entity_type_of_relations

                display_name = (
                    relation.get("entity").get("properties").get("name")
                    if relation.get("entity", {}).get("properties") is not None
                    else relation.get("entity").get("name", "")
                )
                properties = relation.get("entity", {}).get("properties")
                if properties is not None:
                    description = properties.get("description") or ""
                elif properties is None:
                    description = ""
                tags = self.parse_tags(relation.get("entity"))
                related_entities.append(
                    EntitySummary(
                        entity_ref=EntityRef(urn=urn, display_name=display_name),
                        description=description,
                        entity_type=entity_type,
                        tags=tags,
                    )
                )

        relations_return = {relationship_type: related_entities}
        return relations_return

    def list_relations_to_display(
        self, relations: dict[RelationshipType, list[EntitySummary]]
    ) -> dict[RelationshipType, list[EntitySummary]]:
        """
        returns a dict of relationships tagged to display
        """
        relations_to_display = {}

        for key, value in relations.items():
            relations_to_display[key] = [
                entity
                for entity in value
                if "urn:li:tag:dc_display_in_catalogue"
                in [tag.urn for tag in entity.tags]
            ]

        return relations_to_display

    def parse_subtypes(self, entity: dict[str, Any]) -> list[str]:
        subtypes = entity.get("subTypes", {})
        if not subtypes:
            return []
        return subtypes.get("typeNames", [])

    def parse_metadata_last_ingested(self, entity: dict[str, Any]) -> datetime | None:
        """
        Parse the timestamp the metadata was last changed
        """
        timestamp = entity.get("lastIngested")
        if timestamp is None:
            logger.warning("lastIngested timestamp is missing for entity: %r", entity)
            return None
        return timestamp

    def parse_last_datajob_run_date(self, response: dict[str, Any]) -> datetime | None:
        """
        Look for the last job that produced/consumed the dataset and return the time it ran.
        """
        list_of_runs: list = response.get("runs", {}).get("runs", [])
        if not list_of_runs:
            updated = None
        if list_of_runs:
            updated = list_of_runs[0].get("created", {}).get("time", {})

        return updated


class DatasetParser(EntityParser):
    def __init__(self):
        super().__init__()
        self.mapper = None

    def parse(self, result: dict[str, Any]) -> SearchResult:
        matched_fields = self._get_matched_fields(result)
        entity = result["entity"]
        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        tags = self.parse_tags(entity)
        name, display_name, qualified_name = self.parse_names(entity, properties)
        subject_areas = self.parse_subject_areas(entity)

        container = entity.get("container")
        if container:
            _container_name, container_display_name, _container_qualified_name = (
                self.parse_names(container, container.get("properties") or {})
            )

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
            "total_parents": entity.get("relationships", {}).get("total", 0),
        }
        logger.debug(f"{metadata=}")

        metadata.update(custom_properties.usage_restrictions.model_dump())
        metadata.update(custom_properties.access_information.model_dump())
        metadata.update(custom_properties.data_summary.model_dump())

        modified = self.parse_data_last_modified(properties)

        result = SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches=matched_fields,
            name=name,
            display_name=display_name,
            fully_qualified_name=qualified_name,
            parent_entity=(
                EntityRef(urn=container.get("urn"), display_name=container_display_name)
                if container
                else None
            ),
            description=properties.get("description", ""),
            metadata=metadata,
            tags=tags,
            subject_areas=subject_areas,
            glossary_terms=self.parse_glossary_terms(entity),
            last_modified=modified,
        )

        logger.info(f"{result=}")

        return result

    def parse_to_entity_object(self, response: dict, urn: str) -> Table:
        platform_name = response["platform"]["name"]
        properties, custom_properties = self.parse_properties(response)
        columns = self.parse_columns(response)
        subject_areas = self.parse_subject_areas(response)
        owner = self.parse_data_owner(response)
        stewards = self.parse_stewards(response)
        custodians = self.parse_custodians(response)
        tags = self.parse_tags(response)
        glossary_terms = self.parse_glossary_terms(response)
        created = self.parse_data_created(properties)
        name, display_name, qualified_name = self.parse_names(response, properties)

        lineage_relations = self.parse_relations(
            RelationshipType.DATA_LINEAGE,
            [
                response.get("downstream_lineage_relations", {}),
                response.get("upstream_lineage_relations", {}),
            ],
        )

        parent_relations = self.parse_relations(
            RelationshipType.PARENT,
            [response.get("parent_container_relations", {})],
        )
        parent_relations_to_display = self.list_relations_to_display(parent_relations)
        subtypes = self.parse_subtypes(response)

        return Table(
            urn=urn,
            display_name=display_name,
            name=name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            relationships={**lineage_relations, **parent_relations_to_display},
            subject_areas=subject_areas,
            governance=Governance(
                data_owner=owner, data_stewards=stewards, data_custodians=custodians
            ),
            subtypes=subtypes,
            tags=tags,
            glossary_terms=glossary_terms,
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            last_datajob_run_date=self.parse_last_datajob_run_date(response),
            created=created,
            data_last_modified=self.parse_data_last_modified(properties),
            column_details=columns,
            custom_properties=custom_properties,
            platform=EntityRef(display_name=platform_name, urn=platform_name),
        )


class TableParser(DatasetParser):
    def __init__(self):
        super().__init__()
        self.mapper = TableEntityMapping


class ChartParser(DatasetParser):
    def __init__(self):
        super().__init__()
        self.mapper = ChartEntityMapping

    def parse_to_entity_object(self, response, urn):
        properties, custom_properties = self.parse_properties(response)
        name, display_name, qualified_name = self.parse_names(response, properties)
        parent_relations = self.parse_relations(
            RelationshipType.PARENT, [response.get("relationships", {})]
        )

        return Chart(
            urn=urn,
            external_url=properties.get("externalUrl", ""),
            description=properties.get("description", ""),
            name=name,
            display_name=display_name,
            fully_qualified_name=qualified_name,
            subject_areas=self.parse_subject_areas(response),
            governance=Governance(
                data_owner=self.parse_data_owner(response),
                data_stewards=self.parse_stewards(response),
                data_custodians=self.parse_custodians(response),
            ),
            relationships=self.list_relations_to_display(parent_relations),
            tags=self.parse_tags(response),
            glossary_terms=self.parse_glossary_terms(response),
            created=self.parse_data_created(properties),
            data_last_modified=self.parse_data_last_modified(properties),
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            platform=EntityRef(
                display_name=response["platform"]["name"],
                urn=response["platform"]["name"],
            ),
            custom_properties=custom_properties,
        )


class ContainerParser(EntityParser):
    def __init__(self):
        self.mapper = None
        self.matched_fields = {}

    def parse(self, result: dict[str, Any]) -> SearchResult:
        """Map a Container entity to a SearchResult"""
        matched_fields = self._get_matched_fields(result)
        entity = result["entity"]
        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        terms = self.parse_glossary_terms(entity)
        name, display_name, qualified_name = self.parse_names(entity, properties)
        modified = self.parse_data_last_modified(properties)
        subject_areas = self.parse_subject_areas(entity)

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
        }

        metadata.update(custom_properties)

        search_result = SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches=matched_fields,
            name=name,
            fully_qualified_name=qualified_name,
            display_name=display_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=self.parse_tags(entity),
            subject_areas=subject_areas,
            glossary_terms=terms,
            last_modified=modified,
        )

        logger.info(f"{search_result=}")

        return search_result


class DatabaseParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = DatabaseEntityMapping

    def parse_to_entity_object(self, response, urn):
        properties, custom_properties = self.parse_properties(response)
        name, display_name, qualified_name = self.parse_names(response, properties)

        child_relations = self.parse_relations(
            relationship_type=RelationshipType.CHILD,
            relations_list=[response["relationships"]],
            entity_type_of_relations="TABLE",
        )
        relations_to_display = self.list_relations_to_display(child_relations)

        return Database(
            urn=urn,
            display_name=display_name,
            name=name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            relationships=relations_to_display,
            subject_areas=self.parse_subject_areas(response),
            governance=Governance(
                data_owner=self.parse_data_owner(response),
                data_custodians=self.parse_custodians(response),
                data_stewards=self.parse_stewards(response),
            ),
            tags=self.parse_tags(response),
            glossary_terms=self.parse_glossary_terms(response),
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            created=self.parse_data_created(properties),
            data_last_modified=self.parse_data_last_modified(properties),
            custom_properties=custom_properties,
            platform=EntityRef(
                display_name=response["platform"]["name"],
                urn=response["platform"]["name"],
            ),
        )


class PublicationCollectionParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = PublicationCollectionEntityMapping

    def parse_to_entity_object(
        self, response: dict[str, Any], urn: str
    ) -> PublicationCollection:
        properties, custom_properties = self.parse_properties(response)
        name, display_name, qualified_name = self.parse_names(response, properties)

        child_relations = self.parse_relations(
            relationship_type=RelationshipType.CHILD,
            relations_list=[response["relationships"]],
            entity_type_of_relations=PublicationDatasetEntityMapping.url_formatted,
        )
        relations_to_display = self.list_relations_to_display(child_relations)

        return PublicationCollection(
            urn=urn,
            external_url=properties.get("externalUrl", ""),
            display_name=display_name,
            name=name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            relationships=relations_to_display,
            subject_areas=self.parse_subject_areas(response),
            governance=Governance(
                data_owner=self.parse_data_owner(response),
                data_custodians=self.parse_custodians(response),
                data_stewards=self.parse_stewards(response),
            ),
            tags=self.parse_tags(response),
            glossary_terms=self.parse_glossary_terms(response),
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            created=self.parse_data_created(properties),
            data_last_modified=self.parse_data_last_modified(properties),
            custom_properties=custom_properties,
            platform=EntityRef(
                display_name=response["platform"]["name"],
                urn=response["platform"]["name"],
            ),
        )


class PublicationDatasetParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = PublicationDatasetEntityMapping

    def parse_to_entity_object(self, response, urn) -> PublicationDataset:
        properties, custom_properties = self.parse_properties(response)
        name, display_name, qualified_name = self.parse_names(response, properties)

        parent_relations = self.parse_relations(
            RelationshipType.PARENT,
            [response.get("parent_container_relations", {})],
        )
        parent_relations_to_display = self.list_relations_to_display(parent_relations)

        return PublicationDataset(
            urn=urn,
            external_url=properties.get("externalUrl", ""),
            display_name=display_name,
            name=name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            relationships={**parent_relations_to_display},
            subject_areas=self.parse_subject_areas(response),
            governance=Governance(
                data_owner=self.parse_data_owner(response),
                data_custodians=self.parse_custodians(response),
                data_stewards=self.parse_stewards(response),
            ),
            tags=self.parse_tags(response),
            glossary_terms=self.parse_glossary_terms(response),
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            created=self.parse_data_created(properties),
            data_last_modified=self.parse_data_last_modified(properties),
            custom_properties=custom_properties,
            platform=EntityRef(
                display_name=response["platform"]["name"],
                urn=response["platform"]["name"],
            ),
        )


class DashboardParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = DashboardEntityMapping

    def parse_to_entity_object(self, response: dict[str, Any], urn: str) -> Dashboard:
        properties, custom_properties = self.parse_properties(response)
        name, display_name, qualified_name = self.parse_names(response, properties)

        return Dashboard(
            urn=urn,
            display_name=display_name,
            name=name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            relationships=self.list_relations_to_display(
                self.parse_relations(
                    RelationshipType.CHILD, [response["relationships"]]
                )
            ),
            subject_areas=self.parse_subject_areas(response),
            governance=Governance(
                data_owner=self.parse_data_owner(response),
                data_stewards=self.parse_stewards(response),
                data_custodians=self.parse_custodians(response),
            ),
            external_url=properties.get("externalUrl", ""),
            tags=self.parse_tags(response),
            glossary_terms=self.parse_glossary_terms(response),
            metadata_last_ingested=self.parse_metadata_last_ingested(response),
            created=self.parse_data_created(properties),
            data_last_modified=self.parse_data_last_modified(properties),
            custom_properties=custom_properties,
            platform=EntityRef(
                display_name=response["platform"]["name"],
                urn=response["platform"]["name"],
            ),
        )


class GlossaryTermParser(EntityParser):
    def __init__(self):
        super().__init__()
        self.mapper = GlossaryTermEntityMapping

    def parse_to_entity_object(self):
        pass

    def parse(self, entity) -> SearchResult:
        properties, _ = self.parse_properties(entity)
        metadata = {"parentNodes": entity["parentNodes"]["nodes"]}
        name, display_name, qualified_name = self.parse_names(entity, properties)

        return SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches={},
            name=name,
            display_name=display_name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=[],
            last_modified=None,
        )


class EntityParserFactory:
    @staticmethod
    def get_parser(result: dict) -> EntityParser:
        entity = result["entity"]
        entity_type = entity["type"]
        entity_subtype = (
            entity.get("subTypes", {}).get("typeNames", [None])[0]
            if entity.get("subTypes") is not None
            else None
        )

        if entity_type == DatahubEntityType.DATASET.value:
            if entity_subtype == DatahubSubtype.PUBLICATION_DATASET.value:
                return PublicationDatasetParser()
            else:
                return TableParser()
        if entity_type == DatahubEntityType.CHART.value:
            return ChartParser()
        if entity_type == DatahubEntityType.DASHBOARD.value:
            return DashboardParser()
        if entity_type == DatahubEntityType.CONTAINER.value:
            if entity_subtype == DatahubSubtype.PUBLICATION_COLLECTION.value:
                return PublicationCollectionParser()
            else:
                return DatabaseParser()
