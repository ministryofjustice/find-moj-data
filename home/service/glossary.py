from itertools import groupby
from sys import maxsize

from django.core.paginator import Paginator

from datahub_client.entities import (
    ChartEntityMapping,
    DashboardEntityMapping,
    DatabaseEntityMapping,
    PublicationCollectionEntityMapping,
    PublicationDatasetEntityMapping,
    SchemaEntityMapping,
    TableEntityMapping,
)
from datahub_client.search.search_types import MultiSelectFilter, SearchResponse

from .base import GenericService

GLOSSARY_ORDERING = sorted(
    [
        "Data governance",
        "Data protection",
        "Data sources",
        "Electronic monitoring v0.40",
        "Other technical terms",
    ]
)

GLOSSARIES_WITH_ENTITIES = {"Electronic monitoring v0.40"}


class GlossaryService(GenericService):
    def __init__(self):
        self.client = self._get_catalogue_client()
        self.context = self._get_context()

    def _get_context(self):
        """Returns a glossary context which is grouped by parent term"""
        glossary_search_results = self.client.get_glossary_terms()

        def include_term(result):
            parents = result.metadata.get("parentNodes", [])
            if not parents:
                return False
            return parents[0]["properties"]["name"] in GLOSSARY_ORDERING

        def sorter(result):
            first_parent = result.metadata.get("parentNodes", [])
            name = result.name
            parent_index = maxsize
            if first_parent:
                parent_name = first_parent[0]["properties"]["name"]
                try:
                    parent_index = GLOSSARY_ORDERING.index(parent_name)
                except ValueError:
                    pass
            return parent_index, name

        page_results_copy = [
            i for i in glossary_search_results.page_results if include_term(i)
        ]
        page_results_copy.sort(key=sorter)

        def grouper(result):
            first_parent = result.metadata.get("parentNodes", [])
            if first_parent:
                return first_parent[0]["properties"]["name"]
            if not first_parent:
                return "Unsorted"

        page_results_copy = sorted(page_results_copy, key=sorter)
        sorted_total_results = [
            {
                "name": key,
                "members": list(group),
                "has_entities": key in GLOSSARIES_WITH_ENTITIES,
            }
            for key, group in groupby(page_results_copy, key=grouper)
        ]

        # Adding the description in the list comprehension doesn't seem to work
        for parent_term in sorted_total_results:
            if parent_term["members"][0].metadata.get("parentNodes"):
                parent_term["description"] = parent_term["members"][0].metadata[
                    "parentNodes"
                ][0]["properties"]["description"]
            else:
                parent_term["description"] = ""

        context = {"results": sorted_total_results, "h1_value": "Glossary"}

        return context


class GlossaryTermService(GenericService):
    def __init__(self, page, urn):
        self.urn = urn
        self.client = self._get_catalogue_client()
        self.glossary_term = self.client.get_glossary_term_details(urn)
        self.page = page
        self.results = self._get_results(self.page)
        self.paginator = Paginator(list(range(self.results.total_results)), 20)

    def _get_results(self, page) -> SearchResponse:
        """
        Fetch entities linked to the glossary term
        """
        return self.client.search(
            count=20,
            page=str(int(page) - 1),
            result_types=[
                TableEntityMapping,
                ChartEntityMapping,
                DatabaseEntityMapping,
                SchemaEntityMapping,
                DashboardEntityMapping,
                PublicationDatasetEntityMapping,
                PublicationCollectionEntityMapping,
            ],
            filters=[MultiSelectFilter("glossaryTerms", [self.urn])],
        )

    @property
    def context(self):
        return {
            "h1_value": f"{self.glossary_term.display_name} - Glossary term",
            "glossary_term": self.glossary_term,
            "malformed_result_urns": [],
            "results": self.results.page_results,
            "highlighted_results": self.results.page_results,
            "page_obj": self.paginator.get_page(self.page),
            "page_range": self.paginator.get_elided_page_range(  # type: ignore
                self.page, on_each_side=2, on_ends=1
            ),
            "paginator": self.paginator,
            "results_per_page": 20,
            "total_results_str": str(self.results.total_results),
            "total_results": self.results.total_results,
            "readable_match_reasons": {
                "id": "ID",
                "urn": "URN",
                "title": "Title",
                "name": "Name",
                "description": "Description",
                "fieldPaths": "Column name",
                "fieldDescriptions": "Column description",
                "dc_where_to_access_dataset": "Available on",
                "qualifiedName": "Qualified name",
            },
        }
