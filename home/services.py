from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.client.datahub import DataHubCatalogueClient
from django.conf import settings


def get_catalogue_client() -> BaseCatalogueClient:
    return DataHubCatalogueClient(
        jwt_token=settings.DATAHUB_TOKEN, api_url=settings.DATAHUB_URL
    )
