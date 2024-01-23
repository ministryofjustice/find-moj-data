from django.conf import settings
from django.shortcuts import render
from .helper import *
import json

domainlist = {"domainlist": ["HMPPS", "OPG", "HMCTS", "LAA", "Platforms"]}
dpia_list = {"dpia_list": ["Approved", "In progress", "Not required"]}
selected_domain = {"selected_domain": ["HMPPS"]}
selected_dpia = {"selected_dpia": ["Approved"]}

# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def result_view(request):
    context = {}
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render (request, "partial/search_result.html", context)

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
    # For search  page
    search_context = {}
    search_context.update(settings.SAMPLE_SEARCH_RESULTS)
    search_context.update(domainlist)
    search_context.update(dpia_list)
    search_context.update(selected_domain)
    search_context.update(selected_dpia)

    sorted_results=sorted(search_context['results'], key=lambda x: x.get("database_name", ""), reverse=False)
    search_context.update(
            {"results": sorted_results, "total": len(sorted_results)}
        )
    return render(request, "search.html", search_context)
