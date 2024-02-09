from data_platform_catalogue.search_types import MultiSelectFilter, ResultType
from django.core.exceptions import ObjectDoesNotExist

from .base import GenericService


class DetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        filter_value = [MultiSelectFilter("urn", [urn])]
        search_results = self.client.search(
            query="", page=None, filters=filter_value)

        if not search_results.page_results:
            raise ObjectDoesNotExist(urn)

        self.result = search_results.page_results[0]
        self.context = self._get_context()

    def _get_context(self):
        context = {
            "result": self.result,
            "result_type": (
                "Data product"
                if self.result.result_type == ResultType.DATA_PRODUCT
                else "Table"
            ),
            "page_title": f"{self.result.name} - Data catalogue",
        }

        return context
