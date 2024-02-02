from data_platform_catalogue.search_types import (
    MultiSelectFilter, ResultType, SortOption
)
from django.conf import settings
from django.shortcuts import render

from .helper import filter_seleted_domains, get_domain_list
from django.core.paginator import Paginator
from .services import get_catalogue_client


# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)


def details_view(request, id):
    context = {}
    client = get_catalogue_client()
    filter_value = [MultiSelectFilter("urn", id)]
    search_results = client.search(query="", page=None, filters=filter_value)
    result = search_results.page_results[0]
    context["result"] = result
    context["result_type"] = (
        "Data product" if result.result_type == ResultType.DATA_PRODUCT else "Table"
    )
    context["page_title"] = f"{result.name} - Data catalogue"

    return render(request, "details.html", context)


def search_view(request, page: str = "1"):
    
    new_search = request.GET.get("new", "")

    page_for_search = str(int(page) - 1)
    client = get_catalogue_client()
    domain_list = get_domain_list(client)

    context = {}
    context["domainlist"] = domain_list

    domains = request.GET.getlist("domain", [])
    sortby = request.GET.get("sortby", None)
    context["sortby"]=sortby

    if sortby == "ascending":
        sort = SortOption(field="name", ascending=True)
    elif sortby == "descending":
        sort = SortOption(field="name", ascending=False)
    else:
        sort = None

    if domains:
        selected_domain = filter_seleted_domains(domain_list, domains)
        context["selected_domain"] = selected_domain
        request.session["selected_domain"] = selected_domain
        request.session["domains"] = domains
        filter_value = [MultiSelectFilter("domains", domains)]
        query = request.session.get("query", "")
    elif request.GET.get("clear_filter") == "True":
        filter_value = []
        context["selected_domain"] = {}
        request.session["selected_domain"] = {}
        request.session["domains"] = []
        query = request.session.get("query", "")
    elif request.GET.get("clear_label") == "True":
        # Value to clear
        label_value = request.GET.getlist("value")

        # Remove the selected value from list
        domains = request.session.get("domains", None)
        domains = list(set(domains) - set(label_value))
        # Populated selected domain
        selected_domain = filter_seleted_domains(domain_list, domains)
        context["domains"] = domains
        context["selected_domain"] = selected_domain

        # Reassign to session
        request.session["selected_domain"] = selected_domain
        request.session["domains"] = domains
        query = request.session.get("query", "")

        if not domains:
            filter_value = []
        else:
            filter_value = [MultiSelectFilter("domains", domains)]

    elif request.GET.get("query"):
        query=request.GET.get("query")
        print("query", query)
        domains = request.session.get("domains", None)
        request.session["query"] = query
        context["query"] = query
        domains = request.session.get("domains", [])

        # Preserve filter
        selected_domain = filter_seleted_domains(domain_list, domains)
        if not domains:
            filter_value = []
        else:
            context["selected_domain"] = selected_domain
            context["domains"] = domains
            filter_value = [MultiSelectFilter("domains", domains)]
    else:
        if page=="1" and new_search:
            filter_value = []
           
            request.session.clear()
            request.session["domains"] = domains
            context["selected_domain"] = {}
            context["query"]=""
        else:
            domains = request.session.get("domains", [])
            filter_value = []
            context["selected_domain"] = filter_seleted_domains(
                domain_list, domains)
            context["domains"] = domains
            query = request.session.get("query", "")

    # Search with filter
    query = request.GET.get("query", "")
    search_results = client.search(
        query=query, page=page_for_search, filters=filter_value, sort=sort
    )

    items_per_page = 20
    pages_list = list(range(search_results.total_results))
    paginator = Paginator(pages_list, items_per_page)

    context["query"] = query
    context["results"] = search_results.page_results
    context["total_results"] = search_results.total_results
    context["page_obj"] = paginator.get_page(page)
    context["page_range"] = paginator.get_elided_page_range(
        page, on_each_side=2, on_ends=1
    )
    context["paginator"] = paginator
    context["sortby"] = sortby

    if query:
        context["page_title"] = f'Search for "{query}" - Data catalogue'
    else:
        context["page_title"] = "Search - Data catalogue"

    return render(request, "search.html", context)
