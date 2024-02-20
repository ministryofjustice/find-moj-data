from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render

from home.forms.search import SearchForm
from home.service.details import DataProductDetailsService, DatasetDetailsService
from home.service.search import SearchService


def home_view(request):
    context = {}
    return render(request, "home.html", context)


def details_view(request, result_type, id):
    if result_type == "data_product":
        context = data_product_details(request, id)
        return render(request, "details_data_product.html", context)
    if result_type == "table":
        context = dataset_details(request, id)
        return render(request, "details_dataset.html", context)


def data_product_details(request, id):
    try:
        service = DataProductDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def dataset_details(request, id):
    try:
        service = DatasetDetailsService(id)
    except ObjectDoesNotExist:
        raise Http404("Asset does not exist")

    context = service.context

    return context


def search_view(request, page: str = "1"):
    # print(request.GET)
    new_search = request.GET.get("new", "")
    if new_search:
        form = SearchForm()
    else:
        # Populated search scenario
        form = SearchForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest(form.errors)

    search_service = SearchService(form=form, page=page)
    return render(request, "search.html", search_service.context)
