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
            assets_in_data_product.append(
                {
                    "name": result.name,
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
        super().__init__()

        self.client = self._get_catalogue_client()

        self.table_metadata = self.client.get_table_details(urn)

        # Use a search query to obtain the remaining metadata about the table.
        # This could be merged into the above query.
        filter_value = [MultiSelectFilter("urn", [urn])]
        search_results = self.client.search(query="", page=None, filters=filter_value)

        if not search_results.page_results:
            raise ObjectDoesNotExist(urn)

        self.result = search_results.page_results[0]
        data_products = self.result.metadata.get("data_products", ())
        if data_products:
            # Pick the first data product to use as the parent in the breadcrumb.
            # If the dataset belongs to multiple data products, this may diverge
            # from the path the user took to get to this page. However as of datahub
            # v0.12, assigning to multiple data products is not possible.
            self.parent_data_product = data_products[0]
        else:
            self.parent_data_product = None

        self.context = self._get_context()

    def _get_context(self):
        return {
            "table": self.table_metadata,
            "parent_data_product": self.parent_data_product,
            "result": self.result,
        }


class ChartDetailsService(GenericService):
    def __init__(self, urn: str):
        self.client = self._get_catalogue_client()
        self.chart_metadata = self.client.get_chart_details(urn)
        self.context = self._get_context()

    def _get_context(self):
        return {"chart": self.chart_metadata}
