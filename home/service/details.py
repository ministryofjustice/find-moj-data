from data_platform_catalogue.entities import RelationshipType
from data_platform_catalogue.search_types import MultiSelectFilter, ResultType
from django.core.exceptions import ObjectDoesNotExist

from .base import GenericService


class DatabaseDetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        filter_value = [MultiSelectFilter("urn", [urn])]
        search_results = self.client.search(query="", page=None, filters=filter_value)

        if not search_results.page_results:
            raise ObjectDoesNotExist(urn)

        self.result = search_results.page_results[0]
        self.entities_in_database = self._get_database_entities()
        self.context = self._get_context()

    def _get_database_entities(self):
        # we might want to implement pagination for database children
        # details at some point
        database_search = self.client.list_database_tables(
            urn=self.urn, count=500
        ).page_results

        entities_in_database = []
        for result in database_search:
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
            "result": self.result,
            "result_type": "Database",
            "tables": self.entities_in_database,
            "h1_value": "Details",
        }

        return context


class DatasetDetailsService(GenericService):
    def __init__(self, urn: str):
        super().__init__()

        self.client = self._get_catalogue_client()

        self.table_metadata = self.client.get_table_details(urn)

        if not self.table_metadata:
            raise ObjectDoesNotExist(urn)

        self.table_metadata
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
        return {
            "table": self.table_metadata,
            "parent_entity": self.parent_entity,
            "dataset_parent_type": self.dataset_parent_type,
            "h1_value": "Details",
        }


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
