from data_platform_catalogue.search_types import ResultType

from home.service.details import DatasetDetailsService


class TestDetailsDataProductService:
    def test_get_context_data_product(self, detail_dataproduct_context, mock_catalogue):
        assert (
            detail_dataproduct_context["result"]
            == mock_catalogue.search().page_results[0]
        )
        result_type = (
            "Data product"
            if mock_catalogue.search().page_results[0].result_type
            == ResultType.DATA_PRODUCT
            else "Table"
        )
        assert detail_dataproduct_context["result_type"] == result_type
        assert (
            detail_dataproduct_context["page_title"]
            == f"{mock_catalogue.search().page_results[0].name} - Data catalogue"
        )

    def test_get_context_data_product_tables(
        self, detail_dataproduct_context, mock_catalogue
    ):
        name = mock_catalogue.list_data_product_assets().page_results[0].name
        mock_table = {
            "name": name,
            "urn": mock_catalogue.list_data_product_assets().page_results[0].id,
            "description": mock_catalogue.list_data_product_assets()
            .page_results[0]
            .description,
            "type": "TABLE",
        }
        assert detail_dataproduct_context["tables"][0] == mock_table


class TestDetailsDatasetService:
    def test_get_context_contains_table_metadata(self, dataset_with_parent):
        service = DatasetDetailsService(dataset_with_parent["urn"])
        context = service.context
        assert context["table"] == dataset_with_parent["table_metadata"]

    def test_get_context_contains_parent(self, dataset_with_parent):
        service = DatasetDetailsService(dataset_with_parent["urn"])
        context = service.context
        assert (
            context["parent_data_product"] == dataset_with_parent["parent_data_product"]
        )
