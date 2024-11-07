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
    try:
        if result_type == "table":
            service = DatasetDetailsService(urn)
            template = service.template
        elif result_type == "database":
            service = DatabaseDetailsService(urn)
            template = "details_database.html"
        elif result_type == "chart":
            service = ChartDetailsService(urn)
            template = "details_chart.html"
        elif result_type == "dashboard":
            service = DashboardDetailsService(urn)
            template = "details_dashboard.html"
        else:
            raise Http404("Invalid result type")

        return render(request, template, service.context)

    except EntityDoesNotExist:
        raise Http404(f"{result_type} '{urn}' does not exist")


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
