from urllib.parse import urlparse

from data_platform_catalogue.client.exceptions import EntityDoesNotExist
from data_platform_catalogue.search_types import DomainOption
from django.conf import settings
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_control

from home.forms.search import SearchForm
from home.service.details import (
    ChartDetailsService,
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
)
from home.service.domain_fetcher import DomainFetcher
from home.service.glossary import GlossaryService
from home.service.metadata_specification import MetadataSpecificationService
from home.service.search import SearchService


@cache_control(max_age=300, private=True)
def home_view(request):
    """
    Displys only domains that have entities tagged for display in the catalog.
    """
    domains: list[DomainOption] = DomainFetcher().fetch()
    context = {"domains": domains, "h1_value": _("Home")}
    return render(request, "home.html", context)


@cache_control(max_age=300, private=True)
def details_view(request, result_type, urn):
    if result_type == "table":
        service = dataset_service(urn)
        return render(request, service.template, service.context)
    if result_type == "database":
        context = database_details(urn)
        return render(request, "details_database.html", context)
    if result_type == "chart":
        context = chart_details(urn)
        return render(request, "details_chart.html", context)
    if result_type == "dashboard":
        context = dashboard_details(urn)
        return render(request, "details_dashboard.html", context)


def database_details(urn):
    try:
        service = DatabaseDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def dataset_service(urn):
    try:
        service = DatasetDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    return service


def chart_details(urn):
    try:
        service = ChartDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def dashboard_details(urn):
    try:
        service = DashboardDetailsService(urn)
    except EntityDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


@cache_control(max_age=60, private=True)
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


def cookies_view(request):
    valid_domains = [
        urlparse(origin).netloc for origin in settings.CSRF_TRUSTED_ORIGINS
    ]
    referer = request.META.get("HTTP_REFERER")

    if referer:
        referer_domain = urlparse(referer).netloc

        # Validate this referer domain against declared valid domains
        if referer_domain not in valid_domains:
            referer = "/"  # Set to home page if invalid

    context = {
        "previous_page": referer or "/",  # Provide a default fallback if none found
    }
    return render(request, "cookies.html", context)
