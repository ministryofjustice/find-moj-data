import os
from urllib.parse import urlsplit

from data_platform_catalogue.entities import EntityRef, RelationshipType
from data_platform_catalogue.search_types import ResultType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext as _

from ..urns import PlatformUrns
from .base import GenericService


def _parse_parent(relationships: dict) -> EntityRef | None:
    """
    returns the EntityRef of the first parent if one exists
    """
    parents = relationships.get(RelationshipType.PARENT)
    if parents:
        # Pick the first entity to use as the parent in the breadcrumb.
        # If the dataset belongs to multiple parents, this may diverge
        # from the path the user took to get to this page.
        parent_entity = parents[0].entity_ref
    else:
        parent_entity = None
    return parent_entity


def is_access_requirements_a_url(access_requirements) -> bool:
    """
    return a bool indicating if the passed access_requirements arg is a url
    """
    validator = URLValidator()

    try:
        validator(access_requirements)
        is_url = True
    except ValidationError:
        is_url = False

    return is_url


def friendly_platform_name(platform_name):
    if platform_name == "justice-data":
        return "Justice Data"
    else:
        return platform_name


class DatabaseDetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        self.database_metadata = self.client.get_database_details(self.urn)

        if not self.database_metadata:
            raise ObjectDoesNotExist(urn)

        self.is_esda = any(
            term.display_name == "Essential Shared Data Asset (ESDA)"
            for term in self.database_metadata.glossary_terms
        )
        self.entities_in_database = self.database_metadata.relationships[
            RelationshipType.CHILD
        ]
        self.context = self._get_context()
        self.template = "details_database.html"

    def _get_context(self):
        context = {
            "entity": self.database_metadata,
            "entity_type": _("Database"),
            "tables": sorted(
                self.entities_in_database,
                key=lambda d: d.entity_ref.display_name,
            ),
            "h1_value": self.database_metadata.name,
            "is_esda": self.is_esda,
            "is_access_requirements_a_url": is_access_requirements_a_url(
                self.database_metadata.custom_properties.access_information.dc_access_requirements
            ),
            "PlatformUrns": PlatformUrns,
        }

        return context


class DatasetDetailsService(GenericService):
    def __init__(self, urn: str):
        super().__init__()

        self.client = self._get_catalogue_client()

        self.table_metadata = self.client.get_table_details(urn)

        if not self.table_metadata:
            raise ObjectDoesNotExist(urn)

        relationships = self.table_metadata.relationships or {}

        self.parent_entity = _parse_parent(relationships)

        self.context = self._get_context()

        self.template = self._get_template()

    def _get_context(self):
        split_datahub_url = urlsplit(
            os.getenv("CATALOGUE_URL", "https://test-catalogue.gov.uk")
        )

        return {
            "entity": self.table_metadata,
            "entity_type": "Table",
            "parent_entity": self.parent_entity,
            "parent_type": ResultType.DATABASE.name.lower(),
            "h1_value": self.table_metadata.name,
            "has_lineage": self.has_lineage(),
            "lineage_url": f"{split_datahub_url.scheme}://{split_datahub_url.netloc}/dataset/{self.table_metadata.urn}/Lineage?is_lineage_mode=true&",  # noqa: E501
            "is_access_requirements_a_url": is_access_requirements_a_url(
                self.table_metadata.custom_properties.access_information.dc_access_requirements
            ),
            "PlatformUrns": PlatformUrns,
        }

    def _get_template(self):
        return (
            "details_metric.html"
            if "Metric" in self.table_metadata.subtypes
            else "details_table.html"
        )

    def has_lineage(self) -> bool:
        """
        Inspects the relationships property of the Table model to establish if a
        Dataset has any lineage recorded in datahub.
        """
        has_lineage = (
            len(
                self.table_metadata.relationships.get(RelationshipType.DATA_LINEAGE, [])
            )
            > 0
        )
        return has_lineage


class ChartDetailsService(GenericService):
    def __init__(self, urn: str):
        self.client = self._get_catalogue_client()
        self.chart_metadata = self.client.get_chart_details(urn)
        self.parent_entity = _parse_parent(self.chart_metadata.relationships or {})
        self.context = self._get_context()
        self.template = "details_chart.html"

    def _get_context(self):
        return {
            "entity": self.chart_metadata,
            "entity_type": _("Chart"),
            "platform_name": friendly_platform_name(
                self.chart_metadata.platform.display_name
            ),
            "parent_entity": self.parent_entity,
            "parent_type": ResultType.DASHBOARD.name.lower(),
            "h1_value": self.chart_metadata.name,
            "is_access_requirements_a_url": is_access_requirements_a_url(
                self.chart_metadata.custom_properties.access_information.dc_access_requirements
            ),
            "PlatformUrns": PlatformUrns,
        }


class DashboardDetailsService(GenericService):
    def __init__(self, urn: str):
        self.client = self._get_catalogue_client()
        self.dashboard_metadata = self.client.get_dashboard_details(urn)
        self.children = self.dashboard_metadata.relationships[RelationshipType.CHILD]
        self.context = self._get_context()
        self.template = "details_dashboard.html"

    def _get_context(self):

        return {
            "entity": self.dashboard_metadata,
            "entity_type": "Dashboard",
            "h1_value": self.dashboard_metadata.name,
            "platform_name": friendly_platform_name(
                self.dashboard_metadata.platform.display_name
            ),
            "charts": sorted(
                self.children,
                key=lambda d: d.entity_ref.display_name,
            ),
            "is_access_requirements_a_url": is_access_requirements_a_url(
                self.dashboard_metadata.custom_properties.access_information.dc_access_requirements
            ),
            "PlatformUrns": PlatformUrns,
        }


class PublicationCollectionDetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        self.publication_collection_metadata = self.client.get_publication_collection_details(self.urn)

        if not self.publication_collection_metadata:
            raise ObjectDoesNotExist(urn)

        self.entities_in_container = self.publication_collection_metadata.relationships[
            RelationshipType.CHILD
        ]
        self.context = self._get_context()
        self.template = "details_publication_collection.html"

    def _get_context(self):
        context = {
            "entity": self.publication_collection_metadata,
            "entity_type": _("PublicationCollection"),
            "platform_name": friendly_platform_name(
                self.publication_collection_metadata.platform.display_name
            ),
            "publications": sorted(
                self.entities_in_container,
                key=lambda d: d.entity_ref.display_name,
            ),
            "h1_value": self.publication_collection_metadata.name,
            "is_access_requirements_a_url": is_access_requirements_a_url(
                self.publication_collection_metadata.custom_properties.access_information.dc_access_requirements
            ),
        }

        return context

class PublicationDatasetDetailsService(GenericService):
    pass
