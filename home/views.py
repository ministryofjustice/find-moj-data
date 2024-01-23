from django.conf import settings
from django.shortcuts import render
from apps import DataHubGraphQLAPICaller


# Create your views here.
def home_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    return render(request, "home.html", context)


def search_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"

    DataHub_GraphQL_API = DataHubGraphQLAPICaller()
    get_data_products_graphql_response = DataHub_GraphQL_API.get_data_products()

    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render(request, "search.html", context)
