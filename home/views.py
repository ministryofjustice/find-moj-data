from data_platform_catalogue.client.exceptions import EntityDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render

from home.forms.search import SearchForm
from home.models.domain_model import DomainModel
from home.service.details import (
    ChartDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
)
from home.service.glossary import GlossaryService
from home.service.metadata_specification import MetadataSpecificationService
from home.service.search import SearchService
from home.service.search_facet_fetcher import SearchFacetFetcher


def home_view(request):
    facets = SearchFacetFetcher().fetch()
    context = {"domains": DomainModel(facets), "h1_value": "Home"}
    return render(request, "home.html", context)


def details_view(request, result_type, urn):
    if result_type == "table":
        context = dataset_details(urn)
        return render(request, "details_table.html", context)
    if result_type == "database":
        context = database_details(urn)
        return render(request, "details_database.html", context)
    if result_type == "chart":
        context = chart_details(urn)
        return render(request, "details_chart.html", context)


def database_details(urn):
    try:
        service = DatabaseDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def dataset_details(urn):
    try:
        service = DatasetDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def chart_details(urn):
    try:
        service = ChartDetailsService(urn)
    except EntityDoesNotExist:
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


def metadata_specification_view(request):
    metadata_specification = MetadataSpecificationService()
    return render(
        request, "metadata_specification.html", metadata_specification.context
    )
