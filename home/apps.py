from django.apps import AppConfig
import requests
import os

DATAHUB_GRAPHQL_API = os.getenv("DATAHUB_GRAPHQL_API", "https://datahub.apps-tools.development.data-platform.service.justice.gov.uk/api/graphql")
DATAHUB_GRAPHQL_TOKEN = os.getenv("DATAHUB_GRAPHQL_TOKEN", "graphQL api token")


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

class DataHubGraphQLAPICaller:
    def __init__(self) -> None:
        self.api = DATAHUB_GRAPHQL_API
        self.token = DATAHUB_GRAPHQL_TOKEN

    def query_datahub_graphql_api(self, graphql_query) -> requests.Response:
        headers = {"Content-Type": "application/json",  "Authorization": f"Bearer {DATAHUB_GRAPHQL_TOKEN}"}
        json = {"query": graphql_query}

        return requests.post(DATAHUB_GRAPHQL_API, headers=headers, json=json)

    def get_data_products(self) -> requests.Response:
        """Get all data products from the datahub GraphQL API"""
        get_data_products_query = open("core/graphql_queries/get-data-products.graphql").read()

        return self.query_datahub_graphql_api(get_data_products_query)
