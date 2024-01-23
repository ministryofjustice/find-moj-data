from django.conf import settings
from django.shortcuts import render
import requests


# Create your views here.
def home_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    return render(request, "home.html", context)


def search_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"

    url = "https://datahub.apps-tools.development.data-platform.service.justice.gov.uk/api/graphql"
    token = "graphQL api token"
    headers = {"Content-Type": "application/json",  "Authorization": f"Bearer {token}"}
    body = open("home/get-data-products.graphql").read()
    get_data_products_graphql_response = requests.post(url, headers=headers, json={"query": body})

    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render(request, "search.html", context)
