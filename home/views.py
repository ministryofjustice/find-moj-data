from django.shortcuts import render

from home.forms.search import SearchForm
from home.service.search import SearchService


def home_view(request):
    context = {}
    return render(request, "home.html", context)


def details_view(request, id):
    # search_service = SearchService(form)
    # context = search_service.context

    # context = {}
    # # client = get_catalogue_client()
    # filter_value = [MultiSelectFilter("urn", id)]
    # search_results = client.search(query="", page=None, filters=filter_value)
    # result = search_results.page_results[0]
    # context["result"] = result
    # context["result_type"] = (
    #     "Data product" if result.result_type == ResultType.DATA_PRODUCT else "Table"
    # )
    # context["page_title"] = f"{result.name} - Data catalogue"

    # return render(request, "details.html", context)
    pass


def search_view(request, page: str = "1"):
    new_search = request.GET.get("new", "")
    if new_search:
        form = SearchForm()
    else:
        # Populated search scenario
        form = SearchForm(request.GET)
        if not form.is_valid():
            print("form error on validation")
            print(form.errors)

    search_service = SearchService(form=form, page=page)
    return render(request, "search.html", search_service.context)
