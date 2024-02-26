from data_platform_catalogue.search_types import MultiSelectFilter, ResultType
from django.core.exceptions import ObjectDoesNotExist
from copy import deepcopy
from itertools import groupby

from .base import GenericService


class GlossaryService(GenericService):
    def __init__(self):
        # Can we put the client instantiation in the base class?
        self.client = self._get_catalogue_client()
        self.context = self._get_context()

    def _get_context(self):
        glossary_search_results = self.client.get_glossary_terms()
        total_results = glossary_search_results.total_results
        page_results_copy = deepcopy(glossary_search_results.page_results)

        # The sort is required for the grouping to work correctly
        page_results_copy.sort(key=lambda x: x.metadata["parentNodes"][0]["properties"]["name"])
        sorted_total_results = [
            {
                "name": key,
                "members": list(group),
            }
            for key, group
            in groupby(
                page_results_copy,
                key=lambda x:x.metadata["parentNodes"][0]["properties"]["name"]
            )
        ]
        for parent_term in sorted_total_results:
            parent_term["description"] = parent_term["members"][0].metadata["parentNodes"][0]["properties"]["description"]

        context = {"results": sorted_total_results}

        return context

