from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.client.datahub import DataHubCatalogueClient
from django.conf import settings


class GenericService:
    @staticmethod
    def _get_catalogue_client() -> BaseCatalogueClient:
        return DataHubCatalogueClient(
            jwt_token=settings.CATALOGUE_TOKEN, api_url=settings.CATALOGUE_URL
        )
