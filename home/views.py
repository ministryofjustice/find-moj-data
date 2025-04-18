import csv
import logging
from urllib.parse import urlparse

from django.conf import settings
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from datahub_client.entities import (
    ChartEntityMapping,
    DashboardEntityMapping,
    DatabaseEntityMapping,
    PublicationCollectionEntityMapping,
    PublicationDatasetEntityMapping,
    SchemaEntityMapping,
    TableEntityMapping,
)
from datahub_client.exceptions import EntityDoesNotExist
from datahub_client.search.search_types import SubjectAreaOption
from home.forms.search import SearchForm
from home.service.details import (
    ChartDetailsService,
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
    PublicationCollectionDetailsService,
    PublicationDatasetDetailsService,
    SchemaDetailsService,
)
from home.service.details_csv import (
    DashboardDetailsCsvFormatter,
    DatabaseDetailsCsvFormatter,
    DatasetDetailsCsvFormatter,
)
from home.service.glossary import GlossaryService, GlossaryTermService
from home.service.metadata_specification import MetadataSpecificationService
from home.service.search import SearchService
from home.service.subject_area_fetcher import SubjectAreaFetcher

type_details_map = {
    TableEntityMapping.url_formatted: DatasetDetailsService,
    DatabaseEntityMapping.url_formatted: DatabaseDetailsService,
    SchemaEntityMapping.url_formatted: SchemaDetailsService,
    ChartEntityMapping.url_formatted: ChartDetailsService,
    DashboardEntityMapping.url_formatted: DashboardDetailsService,
    PublicationCollectionEntityMapping.url_formatted: PublicationCollectionDetailsService,
    PublicationDatasetEntityMapping.url_formatted: PublicationDatasetDetailsService,
}


@cache_control(max_age=300, private=True)
def home_view(request):
    """
    Displys only subject areas that have entities tagged for display in the catalog.
    """
    subject_areas: list[SubjectAreaOption] = SubjectAreaFetcher().fetch()
    context = {"subject_areas": subject_areas, "h1_value": "Home"}
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
        case TableEntityMapping.url_formatted:
            csv_formatter = DatasetDetailsCsvFormatter(DatasetDetailsService(urn))
        case DatabaseEntityMapping.url_formatted:
            csv_formatter = DatabaseDetailsCsvFormatter(DatabaseDetailsService(urn))
        case SchemaEntityMapping.url_formatted:
            csv_formatter = DatabaseDetailsCsvFormatter(SchemaDetailsService(urn))
        case DashboardEntityMapping.url_formatted:
            csv_formatter = DashboardDetailsCsvFormatter(DashboardDetailsService(urn))
        case _:
            logging.error("Invalid result type for csv details view %s", result_type)
            raise Http404()

    # In case there are any quotes in the filename, remove them in order to
    # not to break the header.
    unsavoury_characters = str.maketrans({'"': ""})
    filename = csv_formatter.filename().translate(unsavoury_characters)

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


def glossary_term_view(request, urn, page="1"):
    service = GlossaryTermService(page, urn)
    return render(request, "glossary_term.html", service.context)


def metadata_specification_view(request):
    metadata_specification = MetadataSpecificationService()
    return render(
        request, "metadata_specification.html", metadata_specification.context
    )


def cookies_view(request):
    valid_subject_areas = [
        urlparse(origin).netloc for origin in settings.CSRF_TRUSTED_ORIGINS
    ]
    referer = request.META.get("HTTP_REFERER")

    if referer:
        referer_domain = urlparse(referer).netloc

        # Validate this referer domain against declared valid domains
        if referer_domain not in valid_subject_areas:
            referer = "/"  # Set to home page if invalid

    context = {
        "previous_page": referer or "/",  # Provide a default fallback if none found
    }
    return render(request, "cookies.html", context)


def accessibility_statement_view(request):
    valid_subject_areas = [
        urlparse(origin).netloc for origin in settings.CSRF_TRUSTED_ORIGINS
    ]
    referer = request.META.get("HTTP_REFERER")

    if referer:
        referer_domain = urlparse(referer).netloc

        # Validate this referer domain against declared valid domains
        if referer_domain not in valid_subject_areas:
            referer = "/"  # Set to home page if invalid

    context = {
        "previous_page": referer or "/",  # Provide a default fallback if none found
        "h1_value": "Accessibility statement",
    }
    return render(request, "accessibility_statement.html", context)
