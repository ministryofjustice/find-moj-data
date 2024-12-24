import logging
from datetime import datetime
from typing import Any, Tuple

from data_platform_catalogue.entities import CustomEntityProperties, AccessInformation, UsageRestrictions, DataSummary, \
    TagRef, FurtherInformation, OwnerRef, GlossaryTermRef, DomainRef, TableEntityMapping, DatabaseEntityMapping, DatahubEntityType, EntityRef
from data_platform_catalogue.search_types import SearchResult

logger = logging.getLogger(__name__)

table_result = {
    'entity': {'urn': 'urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', 'name': 'example_query', 'type': 'DATASET', 'origin': 'PROD', 'uri': None, 'lastIngested': 1734938742935, 'platform': {'urn': 'urn:li:dataPlatform:dbt', 'type': 'DATA_PLATFORM', 'lastIngested': None, 'name': 'dbt', 'properties': {'type': 'OTHERS', 'displayName': 'dbt', 'datasetNameDelimiter': '.', 'logoUrl': '/assets/platforms/dbtlogo.png', '__typename': 'DataPlatformProperties'}, 'displayName': None, 'info': None, '__typename': 'DataPlatform'}, 'dataPlatformInstance': {'urn': 'urn:li:dataPlatformInstance:(urn:li:dataPlatform:dbt,cadet)', 'type': 'DATA_PLATFORM_INSTANCE', 'platform': {'urn': 'urn:li:dataPlatform:dbt', 'type': 'DATA_PLATFORM', 'lastIngested': None, 'name': 'dbt', 'properties': {'type': 'OTHERS', 'displayName': 'dbt', 'datasetNameDelimiter': '.', 'logoUrl': '/assets/platforms/dbtlogo.png', '__typename': 'DataPlatformProperties'}, 'displayName': None, 'info': None, '__typename': 'DataPlatform'}, 'instanceId': 'cadet', '__typename': 'DataPlatformInstance'}, 'platformNativeType': None, 'properties': {'name': 'example_query', 'description': 'Example metric to build the folder structure, can be removed', 'customProperties': [{'key': 'catalog_version', 'value': '1.8.3', '__typename': 'CustomPropertiesEntry'}, {'key': 'audience', 'value': 'Internal', '__typename': 'CustomPropertiesEntry'}, {'key': 'catalog_schema', 'value': 'https://schemas.getdbt.com/dbt/catalog/v1.json', '__typename': 'CustomPropertiesEntry'}, {'key': 'dbt_file_path', 'value': 'models/people/analytical_platform_value_derived/analytical_platform_value_derived__example_query.sql', '__typename': 'CustomPropertiesEntry'}, {'key': 'materialization', 'value': 'table', '__typename': 'CustomPropertiesEntry'}, {'key': 'dc_access_requirements', 'value': 'https://user-guidance.analytical-platform.service.justice.gov.uk/tools/create-a-derived-table/database-access/#database-access', '__typename': 'CustomPropertiesEntry'}, {'key': 'language', 'value': 'sql', '__typename': 'CustomPropertiesEntry'}, {'key': 'dc_where_to_access_dataset', 'value': 'AnalyticalPlatform', '__typename': 'CustomPropertiesEntry'}, {'key': 'dc_slack_channel_name', 'value': '#ask-data-modelling', '__typename': 'CustomPropertiesEntry'}, {'key': 'dc_slack_channel_url', 'value': 'https://moj.enterprise.slack.com/archives/C03J21VFHQ9', '__typename': 'CustomPropertiesEntry'}, {'key': 'node_type', 'value': 'model', '__typename': 'CustomPropertiesEntry'}, {'key': 'dc_data_custodian', 'value': 'holly.furniss', '__typename': 'CustomPropertiesEntry'}, {'key': 'manifest_version', 'value': '1.8.3', '__typename': 'CustomPropertiesEntry'}, {'key': 'manifest_adapter', 'value': 'athena', '__typename': 'CustomPropertiesEntry'}, {'key': 'dbt_package_name', 'value': 'mojap_derived_tables', '__typename': 'CustomPropertiesEntry'}, {'key': 'dbt_unique_id', 'value': 'model.mojap_derived_tables.analytical_platform_value_derived__example_query', '__typename': 'CustomPropertiesEntry'}, {'key': 'manifest_schema', 'value': 'https://schemas.getdbt.com/dbt/manifest/v12.json', '__typename': 'CustomPropertiesEntry'}], 'externalUrl': None, 'lastModified': {'time': 0, 'actor': None, '__typename': 'AuditStamp'}, '__typename': 'DatasetProperties'}, 'structuredProperties': None, 'editableProperties': None, 'ownership': {'owners': [{'owner': {'urn': 'urn:li:corpuser:holly.furniss', 'type': 'CORP_USER', 'username': 'holly.furniss', 'info': {'active': False, 'displayName': 'holly furniss', 'title': None, 'email': 'holly.furniss@justice.gov.uk', 'firstName': None, 'lastName': None, 'fullName': None, '__typename': 'CorpUserInfo'}, 'properties': {'active': False, 'displayName': 'holly furniss', 'title': None, 'email': 'holly.furniss@justice.gov.uk', 'firstName': None, 'lastName': None, 'fullName': None, '__typename': 'CorpUserProperties'}, 'editableProperties': None, '__typename': 'CorpUser'}, 'type': 'DATAOWNER', 'ownershipType': {'urn': 'urn:li:ownershipType:__system__dataowner', 'type': 'CUSTOM_OWNERSHIP_TYPE', 'info': None, 'status': None, '__typename': 'OwnershipTypeEntity'}, 'associatedUrn': 'urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', '__typename': 'Owner'}], 'lastModified': {'time': 0, '__typename': 'AuditStamp'}, '__typename': 'Ownership'}, 'institutionalMemory': None, 'globalTags': {'tags': [{'tag': {'urn': 'urn:li:tag:daily', 'type': 'TAG', 'name': 'daily', 'description': None, 'properties': None, '__typename': 'Tag'}, 'associatedUrn': 'urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', '__typename': 'TagAssociation'}, {'tag': {'urn': 'urn:li:tag:dc_cadet', 'type': 'TAG', 'name': 'dc_cadet', 'description': None, 'properties': None, '__typename': 'Tag'}, 'associatedUrn': 'urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', '__typename': 'TagAssociation'}], '__typename': 'GlobalTags'}, 'glossaryTerms': None, 'subTypes': {'typeNames': ['Model'], '__typename': 'SubTypes'}, 'domain': {'domain': {'urn': 'urn:li:domain:People', 'type': 'DOMAIN', 'properties': {'name': 'People', 'description': None, '__typename': 'DomainProperties'}, 'parentDomains': {'count': 0, 'domains': [], '__typename': 'ParentDomainsResult'}, 'entities': {'total': 184, '__typename': 'SearchResults'}, 'dataProducts': {'total': 0, '__typename': 'SearchResults'}, 'children': {'total': 0, '__typename': 'EntityRelationshipsResult'}, '__typename': 'Domain'}, 'associatedUrn': 'urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', '__typename': 'DomainAssociation'}, 'dataProduct': {'relationships': [], '__typename': 'EntityRelationshipsResult'}, '__typename': 'Dataset', 'container': {'urn': 'urn:li:container:2f60a1d543690979bb961bda0eab1c6f', 'platform': {'urn': 'urn:li:dataPlatform:dbt', 'type': 'DATA_PLATFORM', 'lastIngested': None, 'name': 'dbt', 'properties': {'type': 'OTHERS', 'displayName': 'dbt', 'datasetNameDelimiter': '.', 'logoUrl': '/assets/platforms/dbtlogo.png', '__typename': 'DataPlatformProperties'}, 'displayName': None, 'info': None, '__typename': 'DataPlatform'}, 'properties': {'name': 'analytical_platform_value_derived', '__typename': 'ContainerProperties'}, 'subTypes': {'typeNames': ['Database'], '__typename': 'SubTypes'}, 'deprecation': None, '__typename': 'Container'}, 'deprecation': None, 'embed': None, 'browsePathV2': {'path': [{'name': 'cadet', 'entity': None, '__typename': 'BrowsePathEntry'}, {'name': 'awsdatacatalog', 'entity': None, '__typename': 'BrowsePathEntry'}, {'name': 'analytical_platform_value_derived', 'entity': None, '__typename': 'BrowsePathEntry'}], '__typename': 'BrowsePathV2'}, 'exists': True, 'parentContainers': {'count': 1, 'containers': [{'urn': 'urn:li:container:2f60a1d543690979bb961bda0eab1c6f', 'properties': {'name': 'analytical_platform_value_derived', '__typename': 'ContainerProperties'}, 'subTypes': {'typeNames': ['Database'], '__typename': 'SubTypes'}, '__typename': 'Container'}], '__typename': 'ParentContainersResult'}, 'usageStats': {'buckets': [], 'aggregations': {'uniqueUserCount': 0, 'totalSqlQueries': None, 'fields': [], '__typename': 'UsageQueryResultAggregations'}, '__typename': 'UsageQueryResult'}, 'datasetProfiles': [], 'health': [{'type': 'INCIDENTS', 'status': 'PASS', 'message': None, 'causes': None, '__typename': 'Health'}], 'assertions': {'total': 0, '__typename': 'EntityAssertionsResult'}, 'access': None, 'operations': [], 'viewProperties': {'materialized': True, 'logic': 'asdfasd', 'formattedLogic': None, 'language': 'SQL', '__typename': 'ViewProperties'}, 'autoRenderAspects': [], 'status': {'removed': False, '__typename': 'Status'}, 'runs': {'count': 20, 'start': 0, 'total': 1, '__typename': 'DataProcessInstanceResult'}, 'testResults': None, 'statsSummary': {'queryCountLast30Days': None, 'uniqueUserCountLast30Days': 0, 'topUsersLast30Days': [], '__typename': 'DatasetStatsSummary'}, 'siblings': {'isPrimary': True, '__typename': 'SiblingProperties', 'siblings': [{'urn': 'urn:li:dataset:(urn:li:dataPlatform:athena,athena_cadet.awsdatacatalog.analytical_platform_value_derived.example_query,PROD)', 'type': 'DATASET', 'name': 'athena_cadet.awsdatacatalog.analytical_platform_value_derived.example_query', 'origin': 'PROD', 'uri': None, 'lastIngested': 1734509716880, 'platform': {'urn': 'urn:li:dataPlatform:athena', 'type': 'DATA_PLATFORM', 'lastIngested': None, 'name': 'athena', 'properties': {'type': 'RELATIONAL_DB', 'displayName': 'AWS Athena', 'datasetNameDelimiter': '.', 'logoUrl': '/assets/platforms/awsathenalogo.png', '__typename': 'DataPlatformProperties'}, 'displayName': None, 'info': None, '__typename': 'DataPlatform'}, 'dataPlatformInstance': None, 'platformNativeType': None, 'properties': None, 'structuredProperties': None, 'editableProperties': None, 'ownership': None, 'institutionalMemory': None, 'globalTags': None, 'glossaryTerms': None, 'subTypes': None, 'domain': None, 'dataProduct': {'relationships': [], '__typename': 'EntityRelationshipsResult'}, '__typename': 'Dataset', 'container': None, 'deprecation': None, 'embed': None, 'browsePathV2': {'path': [{'name': 'athena_cadet', 'entity': None, '__typename': 'BrowsePathEntry'}, {'name': 'awsdatacatalog', 'entity': None, '__typename': 'BrowsePathEntry'}, {'name': 'analytical_platform_value_derived', 'entity': None, '__typename': 'BrowsePathEntry'}], '__typename': 'BrowsePathV2'}, 'exists': True, 'parentContainers': {'count': 0, 'containers': [], '__typename': 'ParentContainersResult'}, 'usageStats': {'buckets': [], 'aggregations': {'uniqueUserCount': 0, 'totalSqlQueries': None, 'fields': [], '__typename': 'UsageQueryResultAggregations'}, '__typename': 'UsageQueryResult'}, 'datasetProfiles': [], 'health': [{'type': 'INCIDENTS', 'status': 'PASS', 'message': None, 'causes': None, '__typename': 'Health'}], 'assertions': {'total': 0, '__typename': 'EntityAssertionsResult'}, 'access': None, 'operations': [], 'viewProperties': None, 'autoRenderAspects': [], 'status': None, 'runs': {'count': 20, 'start': 0, 'total': 0, '__typename': 'DataProcessInstanceResult'}, 'testResults': None, 'statsSummary': {'queryCountLast30Days': None, 'uniqueUserCountLast30Days': 0, 'topUsersLast30Days': [], '__typename': 'DatasetStatsSummary'}, 'siblings': {'isPrimary': False, '__typename': 'SiblingProperties'}, 'activeIncidents': {'total': 0, '__typename': 'EntityIncidentsResult'}, 'privileges': {'canEditLineage': False, 'canEditQueries': False, 'canEditEmbed': False, 'canManageEntity': None, 'canManageChildren': None, 'canEditProperties': False, '__typename': 'EntityPrivileges'}, 'forms': None}]}, 'activeIncidents': {'total': 0, '__typename': 'EntityIncidentsResult'}, 'privileges': {'canEditLineage': False, 'canEditQueries': False, 'canEditEmbed': False, 'canManageEntity': None, 'canManageChildren': None, 'canEditProperties': False, '__typename': 'EntityPrivileges'}, 'forms': None}
}
container_result = {
    "data": {
        "entity": {
            "urn": "urn:li:container:2f60a1d543690979bb961bda0eab1c6f",
            "type": "CONTAINER",
            "exists": True,
            "lastIngested": 1735025010359,
            "platform": {
                "urn": "urn:li:dataPlatform:dbt",
                "type": "DATA_PLATFORM",
                "lastIngested": None,
                "name": "dbt",
                "properties": {
                    "type": "OTHERS",
                    "displayName": "dbt",
                    "datasetNameDelimiter": ".",
                    "logoUrl": "/assets/platforms/dbtlogo.png",
                    "__typename": "DataPlatformProperties"
                },
                "displayName": None,
                "info": None,
                "__typename": "DataPlatform"
            },
            "properties": {
                "name": "analytical_platform_value_derived",
                "description": None,
                "externalUrl": None,
                "customProperties": [
                    {
                        "key": "database",
                        "value": "analytical_platform_value_derived",
                        "__typename": "CustomPropertiesEntry"
                    },
                    {
                        "key": "audience",
                        "value": "Internal",
                        "__typename": "CustomPropertiesEntry"
                    },
                    {
                        "key": "instance",
                        "value": "cadet.awsdatacatalog",
                        "__typename": "CustomPropertiesEntry"
                    },
                    {
                        "key": "env",
                        "value": "PROD",
                        "__typename": "CustomPropertiesEntry"
                    },
                    {
                        "key": "platform",
                        "value": "dbt",
                        "__typename": "CustomPropertiesEntry"
                    },
                    {
                        "key": "domain",
                        "value": "people",
                        "__typename": "CustomPropertiesEntry"
                    }
                ],
                "__typename": "ContainerProperties"
            },
            "privileges": {
                "canEditLineage": False,
                "canEditQueries": None,
                "canEditEmbed": None,
                "canManageEntity": None,
                "canManageChildren": None,
                "canEditProperties": False,
                "__typename": "EntityPrivileges"
            },
            "editableProperties": None,
            "ownership": None,
            "tags": {
                "tags": [
                    {
                        "tag": {
                            "urn": "urn:li:tag:People",
                            "type": "TAG",
                            "name": "People",
                            "description": None,
                            "properties": None,
                            "__typename": "Tag"
                        },
                        "associatedUrn": "urn:li:container:2f60a1d543690979bb961bda0eab1c6f",
                        "__typename": "TagAssociation"
                    },
                    {
                        "tag": {
                            "urn": "urn:li:tag:dc_cadet",
                            "type": "TAG",
                            "name": "dc_cadet",
                            "description": None,
                            "properties": None,
                            "__typename": "Tag"
                        },
                        "associatedUrn": "urn:li:container:2f60a1d543690979bb961bda0eab1c6f",
                        "__typename": "TagAssociation"
                    }
                ],
                "__typename": "GlobalTags"
            },
            "institutionalMemory": None,
            "glossaryTerms": None,
            "subTypes": {
                "typeNames": [
                    "Database"
                ],
                "__typename": "SubTypes"
            },
            "entities": {
                "total": 1,
                "__typename": "SearchResults"
            },
            "container": None,
            "parentContainers": {
                "count": 0,
                "containers": [],
                "__typename": "ParentContainersResult"
            },
            "domain": {
                "domain": {
                    "urn": "urn:li:domain:People",
                    "type": "DOMAIN",
                    "properties": {
                        "name": "People",
                        "description": None,
                        "__typename": "DomainProperties"
                    },
                    "parentDomains": {
                        "count": 0,
                        "domains": [],
                        "__typename": "ParentDomainsResult"
                    },
                    "entities": {
                        "total": 184,
                        "__typename": "SearchResults"
                    },
                    "dataProducts": {
                        "total": 0,
                        "__typename": "SearchResults"
                    },
                    "children": {
                        "total": 0,
                        "__typename": "EntityRelationshipsResult"
                    },
                    "__typename": "Domain"
                },
                "associatedUrn": "urn:li:container:2f60a1d543690979bb961bda0eab1c6f",
                "__typename": "DomainAssociation"
            },
            "dataProduct": {
                "relationships": [],
                "__typename": "EntityRelationshipsResult"
            },
            "__typename": "Container",
            "deprecation": None,
            "dataPlatformInstance": {
                "urn": "urn:li:dataPlatformInstance:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog)",
                "type": "DATA_PLATFORM_INSTANCE",
                "platform": {
                    "urn": "urn:li:dataPlatform:dbt",
                    "type": "DATA_PLATFORM",
                    "lastIngested": None,
                    "name": "dbt",
                    "properties": {
                        "type": "OTHERS",
                        "displayName": "dbt",
                        "datasetNameDelimiter": ".",
                        "logoUrl": "/assets/platforms/dbtlogo.png",
                        "__typename": "DataPlatformProperties"
                    },
                    "displayName": None,
                    "info": None,
                    "__typename": "DataPlatform"
                },
                "instanceId": "cadet.awsdatacatalog",
                "__typename": "DataPlatformInstance"
            },
            "status": {
                "removed": False,
                "__typename": "Status"
            },
            "autoRenderAspects": [],
            "structuredProperties": None,
            "forms": None
        }
    },
    "extensions": {}
}


PROPERTIES_EMPTY_STRING_FIELDS = ("description", "externalUrl")
DATA_OWNER = "urn:li:ownershipType:__system__dataowner"
DATA_STEWARD = "urn:li:ownershipType:__system__data_steward"
DATA_CUSTODIAN = "urn:li:ownershipType:data_custodian"


class EntityParser:
    def __init__():
        pass

    def parse(self, search_response):
        raise NotImplementedError

    def parse_names(self,
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

    def parse_tags(self, entity: dict[str, Any]) -> list[TagRef]:
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
        self.mapper = TableEntityMapping
        self.matched_fields = None

    def set_matched_fields(self, matched_fields: dict) -> None:
        self.matched_fields = matched_fields

    def parse(self, entity: dict[str, Any]) -> SearchResult:
        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        tags = self.parse_tags(entity)
        terms = self.parse_glossary_terms(entity)
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

        return SearchResult(
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
            glossary_terms=terms,
            last_modified=modified,
        )


class ContainerParser(EntityParser):
    def __init__(self):
        self.mapper = DatabaseEntityMapping
        self.matched_fields = None

    def set_matched_fields(self, matched_fields: dict) -> None:
        self.matched_fields = matched_fields

    def parse(self, entity: dict[str, Any]) -> SearchResult:
        """Map a Container entity to a SearchResult"""
        owner = self.parse_data_owner(entity)
        properties, custom_properties = self.parse_properties(entity)
        tags = self.parse_tags(entity)
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

        return SearchResult(
            urn=entity["urn"],
            result_type=self.mapper,
            matches=self.matched_fields,
            name=name,
            fully_qualified_name=qualified_name,
            display_name=display_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=tags,
            glossary_terms=terms,
            last_modified=modified,
        )


class EntityParserFactory:
    def __init__(self, result):
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
            return DatasetParser()
        if entity_type == DatahubEntityType.CHART.value:
            return DatasetParser()
        if entity_type == DatahubEntityType.DASHBOARD.value:
            return ContainerParser()
        if entity_type == DatahubEntityType.CONTAINER.value:
            return ContainerParser()


table_parser = EntityParserFactory.get_parser(table_result["entity"])
table = table_parser.parse(table_result["entity"])
print(table)

database_parser = EntityParserFactory.get_parser(container_result["data"]["entity"])
table = database_parser.parse(container_result["data"]["entity"])

print(table)
