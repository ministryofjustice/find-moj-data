import json
import logging
from typing import Sequence

from datahub.configuration.common import ConfigurationError
from datahub.emitter import mce_builder
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
from datahub.metadata import schema_classes
from datahub.metadata.schema_classes import ChangeTypeClass, DomainPropertiesClass

from datahub_client.entities import (
    Chart,
    ChartEntityMapping,
    CustomEntityProperties,
    Dashboard,
    Database,
    DatabaseEntityMapping,
    EntitySummary,
    FindMoJdataEntityMapper,
    PublicationCollection,
    PublicationDataset,
    RelationshipType,
    Table,
    TableEntityMapping,
)
from datahub_client.exceptions import ConnectivityError, EntityDoesNotExist
from datahub_client.graphql.loader import get_graphql_query
from datahub_client.parsers import (
    ChartParser,
    DashboardParser,
    DatabaseParser,
    PublicationCollectionParser,
    PublicationDatasetParser,
    TableParser,
)
from datahub_client.search.search_client import SearchClient
from datahub_client.search.search_types import (
    MultiSelectFilter,
    SearchResponse,
    SortOption,
    SubjectAreaOption,
)

logger = logging.getLogger(__name__)


DATAHUB_DATA_TYPE_MAPPING = {
    "boolean": schema_classes.BooleanTypeClass(),
    "tinyint": schema_classes.NumberTypeClass(),
    "smallint": schema_classes.NumberTypeClass(),
    "int": schema_classes.NumberTypeClass(),
    "integer": schema_classes.NumberTypeClass(),
    "bigint": schema_classes.NumberTypeClass(),
    "double": schema_classes.NumberTypeClass(),
    "float": schema_classes.NumberTypeClass(),
    "decimal": schema_classes.NumberTypeClass(),
    "char": schema_classes.StringTypeClass(),
    "varchar": schema_classes.StringTypeClass(),
    "string": schema_classes.StringTypeClass(),
    "date": schema_classes.DateTypeClass(),
    "timestamp": schema_classes.TimeTypeClass(),
}


class DataHubCatalogueClient:
    """Client for pushing metadata to the DataHub catalogue.

    Tables in the DataHub catalogue are arranged into the following hierarchy:
    DataPlatform -> Dataset

    This client uses the General Metadata Service (GMS, https://datahubproject.io/docs/what/gms/)
    of DataHub to create and update metadata within DataHub. This is implemented in the
    python SDK as the 'python emitter' - https://datahubproject.io/docs/metadata-ingestion/as-a-library.

    If there is a problem communicating with the catalogue, methods will raise an
    instance of CatalogueError.
    """  # noqa: E501

    def __init__(self, jwt_token, api_url: str, graph=None):
        """Create a connection to the DataHub GMS endpoint for class methods to use.

        Args:
            jwt_token: client token for interacting with the provided DataHub instance.
            api_url (str, optional): GMS endpoint for the DataHub instance for the client object.
        """  # noqa: E501
        if api_url.endswith("/"):
            api_url = api_url[:-1]
        if api_url.endswith("/api/gms") or api_url.endswith(":8080"):
            self.gms_endpoint = api_url
        elif api_url.endswith("/api"):
            self.gms_endpoint = api_url + "/gms"
        else:
            raise ConnectivityError("api_url is incorrectly formatted")

        self.server_config = DatahubClientConfig(
            server=self.gms_endpoint, token=jwt_token
        )

        try:
            self.graph = graph or DataHubGraph(self.server_config)
        except ConfigurationError as e:
            raise ConnectivityError from e

        self.search_client = SearchClient(self.graph)

        self.database_query = get_graphql_query("getContainerDetails")
        self.dataset_query = get_graphql_query("getDatasetDetails")
        self.chart_query = get_graphql_query("getChartDetails")
        self.dashboard_query = get_graphql_query("getDashboardDetails")

    def check_entity_exists_by_urn(self, urn: str | None):
        if urn is not None:
            exists = self.graph.exists(entity_urn=urn)
        else:
            exists = False

        return exists

    def create_domain(
        self, domain: str, description: str = "", parent_domain: str | None = None
    ) -> str:
        """Create a Domain, a logical collection of entities

        Args:
            domain (str): name of the new Domain
            description (str, optional): Description of the new Domain. Defaults to "".
            parent_domain (str | None, optional): Declared child relationship to existing Domains.
              Defaults to None.

        Returns:
            str: urn of the created Domain
        """  # noqa: E501
        domain_properties = DomainPropertiesClass(
            name=domain, description=description, parentDomain=parent_domain
        )

        domain_urn = mce_builder.make_domain_urn(domain=domain)

        metadata_event = MetadataChangeProposalWrapper(
            entityType="domain",
            changeType=ChangeTypeClass.UPSERT,
            entityUrn=domain_urn,
            aspect=domain_properties,
        )
        self.graph.emit(metadata_event)

        return domain_urn

    def search(
        self,
        query: str = "*",
        count: int = 20,
        page: str | None = None,
        result_types: Sequence[FindMoJdataEntityMapper] = (
            TableEntityMapping,
            ChartEntityMapping,
            DatabaseEntityMapping,
        ),
        filters: Sequence[MultiSelectFilter] | None = None,
        sort: SortOption | None = None,
    ) -> SearchResponse:
        """
        Wraps the catalogue's search function.
        """
        if filters is None:
            filters = []
        return self.search_client.search(
            query=query,
            count=count,
            page=page,
            result_types=result_types,
            filters=filters,
            sort=sort,
        )

    def list_subject_areas(
        self,
        query: str = "*",
        filters: Sequence[MultiSelectFilter] | None = None,
        count: int = 1000,
    ) -> list[SubjectAreaOption]:
        """
        Returns a list of DomainOption objects
        """
        return self.search_client.list_subject_areas(
            query=query, filters=filters, count=count
        )

    def get_glossary_terms(self, count: int = 1000) -> SearchResponse:
        """Wraps the client's glossary terms query"""
        return self.search_client.get_glossary_terms(count)

    def get_tags(self, count: int = 2000):
        """Wraps the client's get tags query"""
        return self.search_client.get_tags(count)

    def get_table_details(self, urn) -> Table:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.dataset_query, {"urn": urn})[
                "dataset"
            ]
            table_object = TableParser().parse_to_entity_object(response, urn)
            return table_object

        raise EntityDoesNotExist(f"Table with urn: {urn} does not exist")

    def get_chart_details(self, urn) -> Chart:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.chart_query, {"urn": urn})[
                "chart"
            ]
            chart_object = ChartParser().parse_to_entity_object(response, urn)
            return chart_object

        raise EntityDoesNotExist(f"Chart with urn: {urn} does not exist")

    def get_database_details(self, urn: str) -> Database:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.database_query, {"urn": urn})[
                "container"
            ]
            database_object = DatabaseParser().parse_to_entity_object(response, urn)
            return database_object

        raise EntityDoesNotExist(f"Database with urn: {urn} does not exist")

    def get_publication_collection_details(self, urn: str) -> PublicationCollection:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.database_query, {"urn": urn})[
                "container"
            ]
            publication_collection_object = (
                PublicationCollectionParser().parse_to_entity_object(response, urn)
            )
            return publication_collection_object
        raise EntityDoesNotExist(f"Database with urn: {urn} does not exist")

    def get_publication_dataset_details(self, urn: str) -> PublicationDataset:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.dataset_query, {"urn": urn})[
                "dataset"
            ]
            publication_dataset_object = (
                PublicationDatasetParser().parse_to_entity_object(response, urn)
            )
            return publication_dataset_object

        raise EntityDoesNotExist(f"Database with urn: {urn} does not exist")

    def get_dashboard_details(self, urn: str) -> Dashboard:
        if self.check_entity_exists_by_urn(urn):
            response = self.graph.execute_graphql(self.dashboard_query, {"urn": urn})[
                "dashboard"
            ]
            dashboard_object = DashboardParser().parse_to_entity_object(response, urn)
            return dashboard_object

        raise EntityDoesNotExist(f"Dashboard with urn: {urn} does not exist")

    def _get_custom_property_key_value_pairs(
        self,
        custom_properties: CustomEntityProperties,
    ) -> dict:
        """
        get each custom property as an unnested key/value pair.
        we cannot push nested structures to datahub custom properties
        """
        custom_properties_dict = json.loads(
            custom_properties.model_dump_json(), parse_int=str
        )
        custom_properties_unnested = self._flatten_dict(custom_properties_dict)
        custom_properties_unnested_all_string_values = {
            key: str(value) if value is not None else ""
            for key, value in custom_properties_unnested.items()
        }

        return custom_properties_unnested_all_string_values

    def _flatten_dict(self, d, custom_properties=None):
        if custom_properties is None:
            custom_properties = {}
        for key, value in d.items():
            if isinstance(value, dict):
                self._flatten_dict(dict(value.items()), custom_properties)
            else:
                custom_properties[key] = value
        return custom_properties

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


def generate_fqn(parent_name, dataset_name) -> str:
    """
    Generate a fully qualified name for a dataset
    """
    return f"{parent_name}.{dataset_name}"
