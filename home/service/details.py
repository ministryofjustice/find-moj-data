import os
from urllib.parse import urlsplit

from data_platform_catalogue.entities import RelationshipType
from data_platform_catalogue.search_types import ResultType
from django.core.exceptions import ObjectDoesNotExist

from .base import GenericService


def _parse_parent(relationships):
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

    def _get_context(self):
        context = {
            "entity": self.database_metadata,
            "entity_type": "Database",
            "tables": sorted(
                self.entities_in_database,
                key=lambda d: d.entity_ref.display_name,
            ),
            "h1_value": self.database_metadata.name,
            "is_esda": self.is_esda,
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
        }

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

    def _get_context(self):
        return {
            "entity": self.chart_metadata,
            "entity_type": "Chart",
            "parent_entity": self.parent_entity,
            "parent_type": ResultType.DASHBOARD.name.lower(),
            "h1_value": self.chart_metadata.name,
        }


class DashboardDetailsService(GenericService):
    def __init__(self, urn: str):
        self.client = self._get_catalogue_client()
        self.dashboard_metadata = self.client.get_dashboard_details(urn)
        self.children = [
            child
            for child in self.dashboard_metadata.relationships[RelationshipType.CHILD]
            if "urn:li:tag:dc_display_in_catalogue" in [tag.urn for tag in child.tags]
        ]
        self.context = self._get_context()

    def _get_context(self):

        return {
            "entity": self.dashboard_metadata,
            "entity_type": "Dashboard",
            "h1_value": self.dashboard_metadata.name,
            "charts": sorted(
                self.children,
                key=lambda d: d.entity_ref.display_name,
            ),
        }
