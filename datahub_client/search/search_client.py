import json
import logging
from typing import Any, Sequence, Tuple

from datahub.configuration.common import GraphError  # pylint: disable=E0611
from datahub.ingestion.graph.client import DataHubGraph

from datahub_client.entities import (
    ChartEntityMapping,
    DatabaseEntityMapping,
    FindMoJdataEntityMapper,
    SchemaEntityMapping,
    SubjectAreaTaxonomy,
    TableEntityMapping,
)
from datahub_client.exceptions import CatalogueError
from datahub_client.graphql.loader import get_graphql_query
from datahub_client.parsers import EntityParser, EntityParserFactory, GlossaryTermParser
from datahub_client.search.filters import map_filters
from datahub_client.search.search_types import (
    FacetOption,
    MultiSelectFilter,
    SearchFacets,
    SearchResponse,
    SortOption,
    SubjectAreaOption,
)

logger = logging.getLogger(__name__)


class SearchClient:
    def __init__(self, graph: DataHubGraph):
        self.graph = graph
        self.entity_parser = EntityParser()
        self.search_query = get_graphql_query("search")
        self.facets_query = get_graphql_query("facets")
        self.list_subject_areas_query = get_graphql_query("listSubjectAreas")
        self.get_glossary_terms_query = get_graphql_query("getGlossaryTerms")
        self.get_tags_query = get_graphql_query("getTags")

    def search(
        self,
        query: str = "*",
        count: int = 20,
        page: str | None = None,
        result_types: Sequence[FindMoJdataEntityMapper] = (
            TableEntityMapping,
            ChartEntityMapping,
            DatabaseEntityMapping,
            SchemaEntityMapping,
        ),
        filters: Sequence[MultiSelectFilter] | None = None,
        sort: SortOption | None = None,
    ) -> SearchResponse:
        """
        Wraps the catalogue's search function.
        """

        if filters is None:
            filters = []

        start = 0 if page is None else int(page) * count

        entity_type_filters = [
            (
                MultiSelectFilter("_entityType", result.datahub_type.value),
                MultiSelectFilter("typeNames", result.datahub_subtypes),
            )
            for result in result_types
        ]

        formatted_filters = map_filters(filters, entity_type_filters)

        variables = {
            "count": count,
            "query": query,
            "start": start,
            "types": [],
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

        page_results, malformed_result_urns = self._parse_search_results(response)

        return SearchResponse(
            total_results=response["total"],
            page_results=page_results,
            malformed_result_urns=malformed_result_urns,
            facets=self._parse_facets(response.get("facets", [])),
        )

    def _parse_search_results(self, response) -> Tuple[list, list]:
        page_results = []
        malformed_result_urns = []
        parser_factory = EntityParserFactory()

        for result in response["searchResults"]:
            entity_urn = result["entity"]["urn"]
            try:
                parser = parser_factory.get_parser(result)
                parsed_search_result = parser.parse(result)
                page_results.append(parsed_search_result)

            except KeyError as k_e:
                logger.exception(
                    f"Parsing for result {entity_urn} failed, unknown entity type: {k_e}"
                )
                malformed_result_urns.append(entity_urn)
            except Exception:
                logger.exception(f"Parsing for result {entity_urn} failed")
                malformed_result_urns.append(entity_urn)

        return page_results, malformed_result_urns

    def list_subject_areas(
        self,
        query: str = "*",
        filters: Sequence[MultiSelectFilter] | None = None,
        count: int = 1000,
    ):

        formatted_filters = map_filters(filters)
        formatted_filters = formatted_filters[0]["and"]

        variables = {
            "count": count,
            "query": query,
            "filters": formatted_filters,
        }
        try:
            response = self.graph.execute_graphql(
                self.list_subject_areas_query, variables
            )
        except GraphError as e:
            raise CatalogueError("Unable to execute list domains query") from e

        response = response["aggregateAcrossEntities"]
        return self._parse_list_subject_areas(response["facets"])

    def _parse_list_subject_areas(
        self, facets: list[dict[str, Any]]
    ) -> list[SubjectAreaOption]:
        """
        Iterate over all the tag values, and return values for those
        that match the top level subject areas.
        """
        subject_areas: list[SubjectAreaOption] = []

        for aggregation in facets[0]["aggregations"]:
            count = aggregation["count"]
            entity = aggregation["entity"]
            name = EntityParser.parse_name(entity)
            description = EntityParser.parse_description(entity)
            subject_area = SubjectAreaTaxonomy.get_by_name(name)
            if not subject_area:
                continue

            subject_areas.append(
                SubjectAreaOption(subject_area.urn, name, description, count)
            )

        return sorted(subject_areas, key=lambda s: s.name)

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
        parser = GlossaryTermParser()

        for result in response["searchResults"]:
            page_results.append(parser.parse(entity=result["entity"]))

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
