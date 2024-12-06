import csv
import logging
from urllib.parse import urlparse

from data_platform_catalogue.client.exceptions import EntityDoesNotExist
from data_platform_catalogue.entities import EntityTypes
from data_platform_catalogue.search_types import DomainOption
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_control

from home.forms.search import SearchForm
from home.service.details import (
    ChartDetailsService,
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
    PublicationCollectionDetailsService,
    PublicationDatasetDetailsService,
)
from home.service.details_csv import (
    DashboardDetailsCsvFormatter,
    DatabaseDetailsCsvFormatter,
    DatasetDetailsCsvFormatter,
)
from home.service.domain_fetcher import DomainFetcher
from home.service.glossary import GlossaryService
from home.service.metadata_specification import MetadataSpecificationService
from home.service.search import SearchService

type_details_map = {
    EntityTypes.TABLE.url_formatted: DatasetDetailsService,
    EntityTypes.DATABASE.url_formatted: DatabaseDetailsService,
    EntityTypes.CHART.url_formatted: ChartDetailsService,
    EntityTypes.DASHBOARD.url_formatted: DashboardDetailsService,
    EntityTypes.PUBLICATION_COLLECTION.url_formatted: PublicationCollectionDetailsService,
    EntityTypes.PUBLICATION_DATASET.url_formatted: PublicationDatasetDetailsService,
}


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
        service = type_details_map[result_type](urn)
    except KeyError as missing_result_type:
        logging.exception(f"Missing service_details_map for {missing_result_type}")
        raise Http404("Invalid result type")
    except EntityDoesNotExist:
        raise Http404(f"{result_type} '{urn}' does not exist")

    return render(request, service.template, service.context)


@cache_control(max_age=300, private=True)
def details_view_csv(request, result_type, urn) -> HttpResponse:
    match result_type:
        case EntityTypes.TABLE.url_formatted:
            csv_formatter = DatasetDetailsCsvFormatter(DatasetDetailsService(urn))
        case EntityTypes.DATABASE.url_formatted:
            csv_formatter = DatabaseDetailsCsvFormatter(DatabaseDetailsService(urn))
        case EntityTypes.DASHBOARD.url_formatted:
            csv_formatter = DashboardDetailsCsvFormatter(DashboardDetailsService(urn))
        case _:
            logging.error("Invalid result type for csv details view %s", result_type)
            raise Http404()

    # In case there are any quotes in the filename, remove them in order to
    # not to break the header.
    unsavoury_characters = str.maketrans({'"': ""})
    filename = urn.translate(unsavoury_characters) + ".csv"

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
    writer = csv.writer(response)
    writer.writerow(csv_formatter.headers())
    writer.writerows(csv_formatter.data())

    return response


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


def health_view(request):
    """Endpoint for readiness & liveness probe target"""
    return HttpResponse("Ok")
