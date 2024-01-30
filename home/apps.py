from django.apps import AppConfig
import requests
import json
import os

DATAHUB_GRAPHQL_API = os.getenv("DATAHUB_GRAPHQL_API", "https://datahub.apps-tools.development.data-platform.service.justice.gov.uk/api/graphql")
DATAHUB_GRAPHQL_TOKEN = os.getenv("DATAHUB_GRAPHQL_TOKEN", "")


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

class GraphQLError(BaseException):
    pass

class DataHubGraphQLAPICaller:
    def __init__(self) -> None:
        self.api = DATAHUB_GRAPHQL_API
        self.token = DATAHUB_GRAPHQL_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def query_datahub_graphql_api(self, graphql_query) -> requests.Response:
        try:
            json_slug = {"query": graphql_query}
            response = requests.post(self.api, headers=self.headers, json=json_slug)
        except requests.exceptions.RequestException as e:
            raise GraphQLError(e)

        return response

    @staticmethod
    def _get_data_products_query() -> str:
        return open("core/graphql_queries/get-data-products.graphql").read()

    def get_data_products(self) -> dict:
        """Get all data products from the datahub GraphQL API"""
        get_data_products_query = self._get_data_products_query()
        response = self.query_datahub_graphql_api(get_data_products_query)
        data_products_json = json.loads(response.text)
        data_products = data_products_json["data"]["search"]

        return data_products
