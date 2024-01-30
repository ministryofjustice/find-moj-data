from django.conf import settings
from django.shortcuts import render
from home.apps import DataHubGraphQLAPICaller


# Create your views here.
def home_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    return render(request, "home.html", context)


def search_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"

    DataHub_GraphQL_API = DataHubGraphQLAPICaller()
    data_products_json = DataHub_GraphQL_API.get_data_products()

    context.update({"all_data_products": data_products_json["searchResults"]})
    context.update({"num_data_products": data_products_json["total"]})
    return render(request, "search.html", context)
