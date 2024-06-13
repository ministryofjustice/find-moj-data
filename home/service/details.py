import os
from data_platform_catalogue.entities import RelationshipType
from data_platform_catalogue.search_types import ResultType
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import urlsplit

from .base import GenericService


class DatabaseDetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        self.database_metadata = self.client.get_database_details(self.urn)

        if not self.database_metadata:
            raise ObjectDoesNotExist(urn)

        self.is_esda = any(term.display_name == "Essential Shared Data Asset (ESDA)"
            for term in self.database_metadata.glossary_terms)
        self.entities_in_database = self._get_database_entities()
        self.context = self._get_context()

    def _get_database_entities(self):
        # we might want to implement pagination for database children
        # details    at some point
        database_search_results = self.client.list_database_tables(
            urn=self.urn, count=500
        ).page_results

        entities_in_database = []
        for result in database_search_results:
            entities_in_database.append(
                {
                    "name": result.name,
                    "urn": result.urn,
                    "description": result.description,
                    "type": "TABLE",
                }
            )

        entities_in_database = sorted(entities_in_database, key=lambda d: d["name"])

        return entities_in_database

    def _get_context(self):
        context = {
            "database": self.database_metadata,
            "result_type": "Database",
            "tables": self.entities_in_database,
            "h1_value": "Details",
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
        parents = relationships.get(RelationshipType.PARENT)
        if parents:
            # Pick the first entity to use as the parent in the breadcrumb.
            # If the dataset belongs to multiple parents, this may diverge
            # from the path the user took to get to this page.
            self.parent_entity = parents[0]
            self.dataset_parent_type = ResultType.DATABASE.name.lower()
        else:
            self.parent_entity = None
            self.dataset_parent_type = None

        self.context = self._get_context()

    def _get_context(self):
        split_datahub_url = urlsplit(
            os.getenv("CATALOGUE_URL", "https://test-catalogue.gov.uk")
        )

        return {
            "table": self.table_metadata,
            "parent_entity": self.parent_entity,
            "dataset_parent_type": self.dataset_parent_type,
            "h1_value": "Details",
            "has_lineage": self.has_lineage(),
            "lineage_url": f"{split_datahub_url.scheme}://{split_datahub_url.netloc}/dataset/{self.table_metadata.urn}/Lineage?is_lineage_mode=true&",
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
        self.context = self._get_context()

    def _get_context(self):
        return {
            "chart": self.chart_metadata,
            "h1_value": "Details",
        }
