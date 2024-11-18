from collections import defaultdict
from datetime import datetime
from importlib.resources import files
import logging
from typing import Any, Tuple

from data_platform_catalogue.entities import (
    Audience,
    AccessInformation,
    Column,
    ColumnRef,
    CustomEntityProperties,
    DataSummary,
    DomainRef,
    EntityRef,
    EntitySummary,
    FurtherInformation,
    GlossaryTermRef,
    OwnerRef,
    RelationshipType,
    TagRef,
    UsageRestrictions,
)

logger = logging.getLogger(__name__)

PROPERTIES_EMPTY_STRING_FIELDS = ("description", "externalUrl")

# Note: Data owner is missing as an ownershipType entity in Datahub, but it still seems to be
# a system type, and if you set up an add_owner meta mapping in the DBT source, this is what
# gets used by default.
DATA_OWNER = "urn:li:ownershipType:__system__dataowner"
DATA_STEWARD = "urn:li:ownershipType:__system__data_steward"
DATA_CUSTODIAN = "urn:li:ownershipType:data_custodian"


def get_graphql_query(graphql_query_file_name: str) -> str:
    query_text = (
        files("data_platform_catalogue.client.graphql")
        .joinpath(f"{graphql_query_file_name}.graphql")
        .read_text()
    )
    return query_text


def _parse_owner_object(owner: dict):
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
            _make_user_email_from_urn(owner.get("urn")),
        ),
        urn=owner.get("urn", ""),
    )


def parse_data_owner(
    entity: dict[str, Any],
) -> OwnerRef:
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
        return _parse_owner_object(owners[0])
    else:
        return OwnerRef(display_name="", email="", urn="")


def _parse_owners_by_type(
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

    return [_parse_owner_object(owner) for owner in owners]


def parse_custodians(entity: dict[str, Any]) -> list[OwnerRef]:
    """
    Parse ownership information, if it is set, and return a list of data custodians.
    If no owners exist with a matching ownership type, the list will be empty.
    """
    return _parse_owners_by_type(entity, DATA_CUSTODIAN)


def parse_stewards(entity: dict[str, Any]) -> list[OwnerRef]:
    """
    Parse ownership information, if it is set, and return a list of data stewards.
    If no owners exist with a matching ownership type, the list will be empty.
    """
    return _parse_owners_by_type(entity, DATA_STEWARD)


def parse_last_modified(entity: dict[str, Any]) -> datetime | None:
    """
    Parse the last updated timestamp, if available
    """
    timestamp = entity.get("lastIngested")
    if timestamp is None:
        return None
    return timestamp


def parse_created_and_modified(
    properties: dict[str, Any]
) -> Tuple[datetime | None, datetime | None]:
    created = properties.get("created")
    modified = (properties.get("lastModified") or {}).get("time")
    if created == 0:
        created = None
    if modified == 0:
        modified = None

    return created, modified


def parse_updated(
    response: dict[str, Any]
) -> datetime | None:
    list_of_runs: list = response.get("runs", {}).get("runs", [])
    if not list_of_runs:
        updated = None
    if list_of_runs:
        updated = list_of_runs[0].get("created", {}).get("time", {})

    return updated


def parse_tags(entity: dict[str, Any]) -> list[TagRef]:
    """
    Parse tag information into a list of TagRef objects for displaying
    as part of the search result.
    """
    outer_tags = entity.get("tags") or {}
    tags = []
    for tag in outer_tags.get("tags", []):
        properties = tag.get("tag", {}).get("properties", {})
        # This is needed because tags cerated by dbt seemily don't have properties
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


def get_refresh_period_from_cadet_tags(
    tags: list[TagRef],
    refresh_schedules: list[str] = ["daily", "weekly", "monthly"]
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
        refresh_schedule = relevant_refresh_schedules[0].capitalize()
        return refresh_schedule

    if not relevant_refresh_schedules:
        return ""


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


def parse_properties(
    entity: dict[str, Any]
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
    tags = parse_tags(entity)
    cadet_refresh_period = get_refresh_period_from_cadet_tags(tags)
    if cadet_refresh_period:
        data_summary.refresh_period = cadet_refresh_period
    if not cadet_refresh_period:
        data_summary.refresh_period = custom_properties_dict.get("refresh_period", "")
    audience = custom_properties_dict.get("audience", "Internal")

    further_information = FurtherInformation.model_validate(custom_properties_dict)

    custom_properties = CustomEntityProperties(
        access_information=access_information,
        usage_restrictions=usage_restrictions,
        data_summary=data_summary,
        further_information=further_information,
        audience=audience
    )

    return properties, custom_properties


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


def parse_domain(entity: dict[str, Any]) -> DomainRef:
    domain = entity.get("domain") or {}
    inner_domain = domain.get("domain") or {}
    domain_id = inner_domain.get("urn", "")
    if inner_domain:
        domain_properties, _ = parse_properties(inner_domain)
        display_name = domain_properties.get("name", "")
    else:
        display_name = ""

    return DomainRef(display_name=display_name, urn=domain_id)


def parse_columns(entity: dict[str, Any]) -> list[Column]:
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
            ColumnRef(name=foreign_path, display_name=display_name, table=foreign_table)
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


def parse_relations(
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
            description = (
                relation.get("entity").get("properties", {}).get("description", "")
                if relation.get("entity", {}).get("properties") is not None
                else ""
            )
            tags = parse_tags(relation.get("entity"))
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


def _make_user_email_from_urn(urn) -> str:
    """
    Creates a user email using a user entity urn. This should only be called
    when an urn exists for a user that has not signed into datahub via sso,
    so has not been created as an entity and has no associated email address.

    We will look to revist our approach to ownership user creation, see
    github issue https://github.com/ministryofjustice/find-moj-data/issues/578,
    but for now this will fix the issue of owners being flagged in datahub but not
    showing in find-moj-data
    """
    username = urn.replace("urn:li:corpuser:", "")
    email = f"{username}@justice.gov.uk"
    return email


def parse_subtypes(entity: dict[str, Any]) -> list[str]:
    subtypes = entity.get("subTypes", {})
    if not subtypes:
        return []
    return subtypes.get("typeNames", [])
