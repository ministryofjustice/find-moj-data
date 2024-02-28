from copy import deepcopy
from itertools import groupby
from sys import maxsize

from data_platform_catalogue.search_types import MultiSelectFilter, ResultType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .base import GenericService


class GlossaryService(GenericService):
    def __init__(self):
        # Can we put the client instantiation in the base class?
        self.client = self._get_catalogue_client()
        self.context = self._get_context()

    def _get_context(self):
        """Returns a glossary context which is grouped by parent term"""
        glossary_search_results = self.client.get_glossary_terms()

        def sorter(result):
            first_parent = result.metadata.get("parentNodes", [])
            name = result.name
            parent_index = maxsize
            if first_parent:
                parent_name = first_parent[0]["properties"]["name"]
                try:
                    parent_index = settings.GLOSSARY_ORDERING.index(parent_name)
                except ValueError:
                    pass
            return parent_index, name

        def grouper(result):
            first_parent = result.metadata.get("parentNodes", [])
            if first_parent:
                return first_parent[0]["properties"]["name"]
            if not first_parent:
                return "Unsorted"

        page_results_copy = sorted(glossary_search_results.page_results, key=sorter)
        sorted_total_results = [
            {"name": key, "members": list(group)}
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

        context = {"results": sorted_total_results}

        return context
