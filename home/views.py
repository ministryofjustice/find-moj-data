from django.shortcuts import render

from .services import get_catalogue_client


# Create your views here.
def home_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    return render(request, "home.html", context)


def search_view(request):
    query = request.GET.get("query", "")
    page = request.GET.get("page", None)

    client = get_catalogue_client()
    search_results = client.search(query=query, page=page)

    context = {}
    context["query"] = query
    context["service_name"] = "Daap Data Catalogue"
    context["results"] = search_results.page_results
    context["total_results"] = search_results.total_results
    return render(request, "search.html", context)
