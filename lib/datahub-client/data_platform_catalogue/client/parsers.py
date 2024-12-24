import logging
from datetime import datetime
from typing import Any, Tuple

from data_platform_catalogue.entities import CustomEntityProperties, AccessInformation, UsageRestrictions, DataSummary, \
    TagRef, FurtherInformation, OwnerRef, GlossaryTermRef, DomainRef, TableEntityMapping, ChartEntityMapping, \
    DatabaseEntityMapping, DatahubEntityType, EntityRef, PublicationDatasetEntityMapping, DashboardEntityMapping, \
    DatahubSubtype, PublicationCollectionEntityMapping
from data_platform_catalogue.search_types import SearchResult

logger = logging.getLogger(__name__)

PROPERTIES_EMPTY_STRING_FIELDS = ("description", "externalUrl")
DATA_OWNER = "urn:li:ownershipType:__system__dataowner"
DATA_STEWARD = "urn:li:ownershipType:__system__data_steward"
DATA_CUSTODIAN = "urn:li:ownershipType:data_custodian"


class EntityParser:
    def __init__(self):
        pass

    def parse(self, search_response):
        raise NotImplementedError

    def set_matched_fields(self, result: dict) -> None:
        self.matched_fields = self._get_matched_fields(result=result)

    @staticmethod
    def parse_names(entity: dict[str, Any], properties: dict[str, Any]
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

            if properties:
                tags.append(
                    TagRef(
                        display_name=properties.get("name", ""),
                        urn=tag.get("tag", {}).get("urn", ""),
                    )
                )
        return tags

    def parse_domain(self, entity: dict[str, Any]) -> DomainRef:
        domain = entity.get("domain") or {}
        inner_domain = domain.get("domain") or {}
        domain_id = inner_domain.get("urn", "")
        if inner_domain:
            domain_properties, _ = self.parse_properties(inner_domain)
            display_name = domain_properties.get("name", "")
        else:
            display_name = ""

        return DomainRef(display_name=display_name, urn=domain_id)

    @staticmethod
    def get_refresh_period_from_cadet_tags(tags: list[TagRef],
                                           refresh_schedules: tuple[str] = ("daily", "weekly", "monthly")
                                           ) -> str:
        # Check if any of the tags are refresh period tags eg "daily_opg"
        relevant_refresh_schedules = [
            schedule
            for tag_ref in tags
            for schedule in refresh_schedules
            if schedule in tag_ref.display_name
        ]
        if len(relevant_refresh_schedules) > 1:
            logger.warn(f"More than one refresh period tag found: {tags=}")

        if relevant_refresh_schedules:
            refresh_schedule = ", ".join(relevant_refresh_schedules).capitalize()
            return refresh_schedule

        if not relevant_refresh_schedules:
            return ""

    def parse_properties(self, entity: dict[str, Any]) -> Tuple[dict[str, Any], CustomEntityProperties]:
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


class DatasetParser(EntityParser):
    def __init__(self):
        super().__init__()
        self.mapper = None

    def parse(self, entity: dict[str, Any]) -> SearchResult:

        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        tags = self.parse_tags(entity)
        name, display_name, qualified_name = self.parse_names(entity, properties)
        domain = self.parse_domain(entity)


        container = entity.get("container")
        if container:
            _container_name, container_display_name, _container_qualified_name = (
                self.parse_names(container, container.get("properties") or {})
            )

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
            "total_parents": entity.get("relationships", {}).get("total", 0),
            "domain_name": domain.display_name,
            "domain_id": domain.urn,
        }
        logger.debug(f"{metadata=}")

        metadata.update(custom_properties.usage_restrictions.model_dump())
        metadata.update(custom_properties.access_information.model_dump())
        metadata.update(custom_properties.data_summary.model_dump())

        modified = self.parse_data_last_modified(properties)

        result = SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches=self.matched_fields,
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
            glossary_terms=self.parse_glossary_terms(entity),
            last_modified=modified,
        )

        logger.info(f"{result=}")

        return result


class TableParser(DatasetParser):
    def __init__(self):
        super().__init__()
        self.mapper = TableEntityMapping


class ChartParser(DatasetParser):
    def __init__(self):
        super().__init__()
        self.mapper = ChartEntityMapping


class PublicationDatasetParser(DatasetParser):
    def __init__(self):
        super().__init__()
        self.mapper = PublicationDatasetEntityMapping


class ContainerParser(EntityParser):
    def __init__(self):
        self.mapper = None
        self.matched_fields = {}

    def parse(self, entity: dict[str, Any]) -> SearchResult:
        """Map a Container entity to a SearchResult"""
        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        terms = self.parse_glossary_terms(entity)
        name, display_name, qualified_name = self.parse_names(entity, properties)
        modified = self.parse_data_last_modified(properties)
        domain = self.parse_domain(entity)

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
            "domain_name": domain.display_name,
            "domain_id": domain.urn,
        }

        metadata.update(custom_properties)

        result = SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches=self.matched_fields,
            name=name,
            fully_qualified_name=qualified_name,
            display_name=display_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=self.parse_tags(entity),
            glossary_terms=terms,
            last_modified=modified,
        )

        logger.info(f"{result=}")

        return result


class DatabaseParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = DatabaseEntityMapping


class PublicationCollectionParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = PublicationCollectionEntityMapping

class DashboardParser(ContainerParser):
    def __init__(self):
        super().__init__()
        self.mapper = DashboardEntityMapping

class EntityParserFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_parser(entity: dict) -> EntityParser:
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
