from django.conf import settings

from datahub_client.client import DataHubCatalogueClient


class GenericService:
    @staticmethod
    def _get_catalogue_client() -> DataHubCatalogueClient:
        return DataHubCatalogueClient(
            jwt_token=settings.CATALOGUE_TOKEN, api_url=settings.CATALOGUE_URL
        )
