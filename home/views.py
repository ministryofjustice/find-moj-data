from django.conf import settings
from django.shortcuts import render
from .services import get_catalogue_client

domainlist = {"domainlist": ["HMPPS", "OPG", "HMCTS", "LAA", "Platforms"]}
dpia_list = {"dpia_list": ["Approved", "In progress", "Not required"]}
selected_domain = {"selected_domain": ["HMPPS"]}
selected_dpia = {"selected_dpia": ["Approved"]}

# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def details_view(request):
    context = {}
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    context.update(
            {"result": context["results"][1]}
        )
    return render(request, "details.html", context)

def result_view(request):
    context = {}
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    context.update(domainlist)
    context.update(dpia_list)
    return render (request, "search.html", context)

def filter_view(request):
   
    # Check if we can reload partial search_html page alone
    data = {}
    data.update(settings.SAMPLE_SEARCH_RESULTS)

    search_context = {}
    search_context.update(domainlist)
    search_context.update(dpia_list)
   
    if request.method == "POST":
        # data = json.loads(request.body.decode('utf-8'))
        # print(data.get('href_value'))
        domain = request.POST.getlist("type")
        dpia = request.POST.getlist("dpia")

        filtered_results = [
            item
            for item in data["results"]
            if (not domain or (item["domain_name"]).lower() in domain)
            and (not dpia or (item["dpia"]).lower() in dpia)
        ]

        sorted_results=sorted(filtered_results, key=lambda x: x.get("database_name", ""), reverse=False)

        search_context.update(
            {"results": sorted_results, "total": len(filtered_results)}
        )

        selected_domain = {"selected_domain": domain}
        search_context.update(selected_domain)
        selected_dpia = {"selected_dpia": dpia}
        search_context.update(selected_dpia)

    return render (request, "search.html", search_context)


def search_view(request):
    query = request.GET.get("query", "")
    page = request.GET.get("page", None)

    client = get_catalogue_client()
    search_results = client.search(query=query, page=page)
   
    context = {}
    context.update(domainlist)
    context.update(dpia_list)

    context["query"] = query
    context["service_name"] = "Daap Data Catalogue"
    context["results"] = search_results.page_results
    context["total_results"] = search_results.total_results
    return render(request, "search.html", context)
    # # For search  page
    # search_context = {}
    # search_context.update(settings.SAMPLE_SEARCH_RESULTS)
  

    # sorted_results=sorted(search_context['results'], key=lambda x: x.get("database_name", ""), reverse=False)
    # search_context.update(
    #         {"results": sorted_results, "total": len(sorted_results)}
    #     )
    # return render(request, "search.html", search_context)