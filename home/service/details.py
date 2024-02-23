from data_platform_catalogue.search_types import MultiSelectFilter, ResultType
from django.core.exceptions import ObjectDoesNotExist


from .base import GenericService


class DataProductDetailsService(GenericService):
    def __init__(self, urn: str):
        self.urn = urn
        self.client = self._get_catalogue_client()

        filter_value = [MultiSelectFilter("urn", [urn])]
        search_results = self.client.search(query="", page=None, filters=filter_value)

        if not search_results.page_results:
            raise ObjectDoesNotExist(urn)

        self.result = search_results.page_results[0]
        self.data_product_name = self.result.name
        self.assets_in_data_product = self._get_data_product_entities()
        self.context = self._get_context()

    def _get_data_product_entities(self):
        # we might want to implement pagination for data product children
        # details at some point
        data_product_search = self.client.list_data_product_assets(
            urn=self.urn, count=500
        ).page_results

        assets_in_data_product = []
        for result in data_product_search:
            # name is like that as fully qualified name ({data_product}.{asset}) seems
            # too verbose to display here.
            assets_in_data_product.append(
                {
                    "name": (
                        result.name
                        if not result.name.split(".")[0] == self.data_product_name
                        else result.name.split(".")[1]
                    ),
                    "urn": result.id,
                    "description": result.description,
                    "type": "TABLE",
                }
            )

        assets_in_data_product = sorted(assets_in_data_product, key=lambda d: d["name"])

        return assets_in_data_product

    def _get_context(self):
        context = {
            "result": self.result,
            "result_type": (
                "Data product"
                if self.result.result_type == ResultType.DATA_PRODUCT
                else "Table"
            ),
            "tables": self.assets_in_data_product,
            "page_title": f"{self.result.name} - Data catalogue",
        }

        return context


class DatasetDetailsService(GenericService):
    def __init__(self, urn: str):
        self.context = self._get_context()

    def _get_context(self):
        return {}
