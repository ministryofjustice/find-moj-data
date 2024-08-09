import json
import logging
from importlib.resources import files
from typing import Any, Sequence, Tuple

from datahub.configuration.common import GraphError  # pylint: disable=E0611
from datahub.ingestion.graph.client import DataHubGraph  # pylint: disable=E0611

from data_platform_catalogue.client.exceptions import CatalogueError
from data_platform_catalogue.client.graphql_helpers import (
    parse_created_and_modified,
    parse_domain,
    parse_glossary_terms,
    parse_last_modified,
    parse_names,
    parse_owner,
    parse_properties,
    parse_tags,
)
from data_platform_catalogue.entities import EntityRef
from data_platform_catalogue.search_types import (
    DomainOption,
    FacetOption,
    MultiSelectFilter,
    ResultType,
    SearchFacets,
    SearchResponse,
    SearchResult,
    SortOption,
)
from pydantic_core import ValidationError

logger = logging.getLogger(__name__)


class SearchClient:
    def __init__(self, graph: DataHubGraph):
        self.graph = graph
        self.search_query = self.get_graphql_query("search")
        self.facets_query = self.get_graphql_query("facets")
        self.list_domains_query = self.get_graphql_query("listDomains")
        self.get_glossary_terms_query = self.get_graphql_query("getGlossaryTerms")
        self.get_tags_query = self.get_graphql_query("getTags")

    @staticmethod
    def get_graphql_query(graphql_query_file_name: str) -> str:
        query_text = (
            files("data_platform_catalogue.client.graphql")
            .joinpath(f"{graphql_query_file_name}.graphql")
            .read_text()
        )
        return query_text

    def search(
        self,
        query: str = "*",
        count: int = 20,
        page: str | None = None,
        result_types: Sequence[ResultType] = (
            ResultType.TABLE,
            ResultType.CHART,
            ResultType.DATABASE,
        ),
        filters: Sequence[MultiSelectFilter] = [],
        sort: SortOption | None = None,
    ) -> SearchResponse:
        """
        Wraps the catalogue's search function.
        """

        start = 0 if page is None else int(page) * count

        types = self._map_result_types(result_types)
        logger.debug(f"Getting facets with result types {types}")

        # This is the tag that any and every entity we want to present in search results
        # now must have.
        display_in_catalogue_filter = MultiSelectFilter(
            filter_name="tags", included_values=["urn:li:tag:dc_display_in_catalogue"]
        )

        filters.append(display_in_catalogue_filter)
        formatted_filters = self._map_filters(filters)

        variables = {
            "count": count,
            "query": query,
            "start": start,
            "types": types,
            "filters": formatted_filters,
        }

        if sort:
            variables.update({"sort": sort.format()})

        try:
            response = self.graph.execute_graphql(self.search_query, variables)
        except GraphError as e:
            raise CatalogueError("Unable to execute search query") from e

        response = response["searchAcrossEntities"]
        if response["total"] == 0:
            return SearchResponse(total_results=0, page_results=[])

        logger.debug(json.dumps(response, indent=2))

        # Should these 2 variables be bound or unbound?
        page_results, malformed_result_urns = self._parse_search_results(response)

        return SearchResponse(
            total_results=response["total"],
            page_results=page_results,
            malformed_result_urns=malformed_result_urns,
            facets=self._parse_facets(response.get("facets", [])),
        )

    def _parse_search_results(self, response) -> Tuple[list, list]:
        self.page_results = []
        self.malformed_result_urns = []
        for result in response["searchResults"]:
            self._parse_result(result)

        return self.page_results, self.malformed_result_urns

    def _parse_result(self, result):
        entity = result["entity"]
        entity_type = entity["type"]
        entity_urn = entity["urn"]
        matched_fields = self._get_matched_fields(result=result)

        if entity_type == "DATASET":
            try:
                parsed_result = self._parse_dataset(entity, matched_fields, ResultType.TABLE)
                self.page_results.append(parsed_result)
            except Exception:
                logger.warn(f"Parsing for result {entity_urn} failed")
                self.malformed_result_urns.append(entity_urn)
        elif entity_type == "CHART":
            try:
                parsed_result = self._parse_dataset(entity, matched_fields, ResultType.CHART)
                self.page_results.append(parsed_result)
            except Exception:
                logger.warn(f"Parsing for result {entity_urn} failed")
                self.malformed_result_urns.append(entity_urn)
        elif entity_type == "CONTAINER":
            try:
                parsed_result = self._parse_container(entity, matched_fields, ResultType.DATABASE)
                self.page_results.append(parsed_result)
            except Exception:
                logger.warn(f"Parsing for result {entity_urn} failed")
                self.malformed_result_urns.append(entity_urn)
        elif entity_type in "DASHBOARD":
            try:
                parsed_result = self._parse_container(entity, matched_fields, ResultType.DASHBOARD)
                self.page_results.append(parsed_result)
            except Exception:
                logger.warn(f"Parsing for result {entity_urn} failed")
                self.malformed_result_urns.append(entity_urn)
        else:
            logger.error(f"Unexpected entity type: {entity_type}")
            raise ValueError(f"Unexpected entity type: {entity_type}")

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

    def search_facets(
        self,
        query: str = "*",
        result_types: Sequence[ResultType] = (ResultType.TABLE,),
        filters: Sequence[MultiSelectFilter] = (),
    ) -> SearchFacets:
        """
        Returns facets that can be used to filter the search results.
        """
        types = self._map_result_types(result_types)
        formatted_filters = self._map_filters(filters)

        variables = {
            "query": query,
            "facets": [],
            "types": types,
            "filters": formatted_filters,
        }

        try:
            response = self.graph.execute_graphql(self.facets_query, variables)
        except GraphError as e:
            raise CatalogueError("Unable to execute facets query") from e

        response = response["aggregateAcrossEntities"]
        return self._parse_facets(response.get("facets", []))

    def list_domains(
        self,
        query: str = "*",
        filters: Sequence[MultiSelectFilter] = [
            MultiSelectFilter("tags", ["urn:li:tag:dc_display_in_catalogue"])
        ],
        count: int = 1000,
    ) -> list[DomainOption]:
        """
        Returns domains that can be used to filter the search results.
        """
        formatted_filters = self._map_filters(filters)

        variables = {
            "count": count,
            "query": query,
            "filters": formatted_filters,
        }

        try:
            response = self.graph.execute_graphql(self.list_domains_query, variables)
        except GraphError as e:
            raise CatalogueError("Unable to execute list domains query") from e

        response = response["listDomains"]
        return self._parse_list_domains(response.get("domains"))

    def _get_data_collection_page_results(self, response, key_for_results: str):
        """
        for use by entities that hold collections of data, eg. container
        """
        page_results = []
        for result in response[key_for_results]["searchResults"]:
            entity = result["entity"]
            entity_type = entity["type"]
            matched_fields: dict = {}
            if entity_type == "DATASET":
                page_results.append(
                    self._parse_dataset(entity, matched_fields, ResultType.TABLE)
                )
            else:
                raise ValueError(f"Unexpected entity type: {entity_type}")
        return page_results

    def _map_result_types(self, result_types: Sequence[ResultType]):
        """
        Map result types to Datahub EntityTypes
        """
        types = []
        if ResultType.TABLE in result_types:
            types.append("DATASET")
        if ResultType.GLOSSARY_TERM in result_types:
            types.append("GLOSSARY_TERM")
        if ResultType.CHART in result_types:
            types.append("CHART")
        if ResultType.DATABASE in result_types:
            types.append("CONTAINER")
        if ResultType.DASHBOARD in result_types:
            types.append("DASHBOARD")

        return types

    def _map_filters(self, filters: Sequence[MultiSelectFilter]):
        result = [
            {"field": filter.filter_name, "values": filter.included_values}
            for filter in filters
        ]
        return result

    def _parse_list_domains(
        self, list_domains_result: list[dict[str, Any]]
    ) -> list[DomainOption]:
        list_domain_options: list[DomainOption] = []

        for domain in list_domains_result:
            urn = domain.get("urn", "")
            properties = domain.get("properties", {})
            name = properties.get("name", "")
            entities = domain.get("entities", {})
            total = entities.get("total", 0)

            list_domain_options.append(DomainOption(urn, name, total))
        return list_domain_options

    def _parse_dataset(
        self, entity: dict[str, Any], matches, result_type: ResultType
    ) -> SearchResult:
        """
        Map a dataset entity to a SearchResult
        """
        owner = parse_owner(entity)
        properties, custom_properties = parse_properties(entity)
        tags = parse_tags(entity)
        terms = parse_glossary_terms(entity)
        last_modified = parse_last_modified(entity)
        name, display_name, qualified_name = parse_names(entity, properties)
        container = entity.get("container")
        if container:
            _container_name, container_display_name, _container_qualified_name = (
                parse_names(container, container.get("properties") or {})
            )
        domain = parse_domain(entity)

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
            "total_parents": entity.get("relationships", {}).get("total", 0),
            "domain_name": domain.display_name,
            "domain_id": domain.urn,
            "entity_types": self._parse_types_and_sub_types(entity, "Dataset"),
        }
        logger.debug(f"{metadata=}")

        metadata.update(custom_properties.usage_restrictions.model_dump())
        metadata.update(custom_properties.access_information.model_dump())
        metadata.update(custom_properties.data_summary.model_dump())

        _, modified = parse_created_and_modified(properties)

        return SearchResult(
            urn=entity["urn"],
            result_type=result_type,
            matches=matches,
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
            last_modified=modified or last_modified,
        )

    def _parse_facets(self, facets: list[dict[str, Any]]) -> SearchFacets:
        """
        Parse the facets and aggregate information from the query results
        """
        results = {}
        for facet in facets:
            field = facet["field"]
            if field not in ("domains", "tags", "customProperties", "glossaryTerms"):
                continue

            options = []
            for aggregate in facet["aggregations"]:
                value = aggregate["value"]
                count = aggregate["count"]
                entity = aggregate.get("entity") or {}
                properties = entity.get("properties") or {}
                label = properties.get("name", value)
                options.append(FacetOption(value=value, label=label, count=count))

            results[field] = options

        return SearchFacets(results)

    def _parse_glossary_term(self, entity) -> SearchResult:
        properties, _ = parse_properties(entity)
        metadata = {"parentNodes": entity["parentNodes"]["nodes"]}
        name, display_name, qualified_name = parse_names(entity, properties)

        return SearchResult(
            urn=entity["urn"],
            result_type=ResultType.GLOSSARY_TERM,
            matches={},
            name=name,
            display_name=display_name,
            fully_qualified_name=qualified_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=[],
            last_modified=None,
        )

    def get_glossary_terms(self, count: int = 1000) -> SearchResponse:
        "Get some number of glossary terms from DataHub"
        variables = {"count": count}
        try:
            response = self.graph.execute_graphql(
                self.get_glossary_terms_query, variables
            )
        except GraphError as e:
            raise CatalogueError("Unable to execute getGlossaryTerms query") from e

        page_results = []
        response = response["searchAcrossEntities"]
        logger.debug(json.dumps(response, indent=2))

        for result in response["searchResults"]:
            page_results.append(self._parse_glossary_term(entity=result["entity"]))

        return SearchResponse(
            total_results=response["total"], page_results=page_results
        )

    def get_tags(self, count: int = 2000):
        """
        gets a list of tag urns from datahub.

        If the total tags in datahub is more
        than 2000 (we have too many tags) but the count should be increased to get
        all tags
        """
        variables = {"count": count}
        try:
            response = self.graph.execute_graphql(self.get_tags_query, variables)
        except GraphError as e:
            raise CatalogueError("Unable to execute getTags query") from e

        response = response["searchAcrossEntities"]
        logger.debug(json.dumps(response, indent=2))

        return self._parse_global_tags(response)

    def _parse_global_tags(self, tag_query_results) -> list[tuple[str, str]]:
        """parse results of get tags query"""

        # name properties of tags are often not set, i.e. all those from dbt
        # so better to get tag name from tag urn.
        tags_list = [
            (tag["entity"]["urn"].replace("urn:li:tag:", ""), tag["entity"]["urn"])
            for tag in tag_query_results["searchResults"]
        ]
        return tags_list

    def _parse_container(
        self, entity: dict[str, Any], matches, subtype: ResultType
    ) -> SearchResult:
        """
        Map a Container entity to a SearchResult
        """
        tags = parse_tags(entity)
        terms = parse_glossary_terms(entity)
        last_modified = parse_last_modified(entity)
        properties, custom_properties = parse_properties(entity)
        domain = parse_domain(entity)
        owner = parse_owner(entity)
        name, display_name, qualified_name = parse_names(entity, properties)

        metadata = {
            "owner": owner.display_name,
            "owner_email": owner.email,
            "domain_name": domain.display_name,
            "domain_id": domain.urn,
            "entity_types": self._parse_types_and_sub_types(entity, "Container"),
        }

        metadata.update(custom_properties)

        return SearchResult(
            urn=entity["urn"],
            result_type=subtype,
            matches=matches,
            name=name,
            fully_qualified_name=qualified_name,
            display_name=display_name,
            description=properties.get("description", ""),
            metadata=metadata,
            tags=tags,
            glossary_terms=terms,
            last_modified=last_modified,
        )

    def _parse_types_and_sub_types(self, entity: dict, entity_type: str) -> dict:
        entity_sub_type = (
            entity.get("subTypes", {}).get("typeNames", [entity_type])
            if entity.get("subTypes") is not None
            else [entity_type]
        )
        return {"entity_type": entity_type, "entity_sub_types": entity_sub_type}
