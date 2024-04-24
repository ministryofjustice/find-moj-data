from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render

from home.forms.search import SearchForm
from home.service.details import (
    ChartDetailsService,
    DatabaseDetailsService,
    DataProductDetailsService,
    DatasetDetailsService,
)
from home.service.glossary import GlossaryService
from home.service.search import SearchService


def home_view(request):
    context = {}
    context["h1_value"] = "Home"
    return render(request, "home.html", context)


def details_view(request, result_type, id):
    if result_type == "data_product":
        context = data_product_details(id)
        return render(request, "details_data_product.html", context)
    if result_type == "table":
        context = dataset_details(id)
        return render(request, "details_table.html", context)
    if result_type == "database":
        context = database_details(id)
        return render(request, "details_database.html", context)
    if result_type == "chart":
        context = chart_details(id)
        return render(request, "details_chart.html", context)


def data_product_details(id):
    try:
        service = DataProductDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def database_details(id):
    try:
        service = DatabaseDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def dataset_details(id):
    try:
        service = DatasetDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def chart_details(id):
    try:
        service = ChartDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def search_view(request, page: str = "1"):
    new_search = request.GET.get("new", "")
    request.session["last_search"] = ""
    if new_search:
        form = SearchForm()
    else:
        # Populated search scenario
        form = SearchForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors)

        request.session["last_search"] = request.GET.urlencode()

    search_service = SearchService(form=form, page=page)
    return render(request, "search.html", search_service.context)


def glossary_view(request):
    glossary_service = GlossaryService()
    return render(request, "glossary.html", glossary_service.context)
