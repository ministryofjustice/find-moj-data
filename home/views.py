from django.conf import settings
from django.shortcuts import render
from .services import get_catalogue_client
from data_platform_catalogue.search_types import MultiSelectFilter



# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def details_view(request):
    id=request.GET.get('id')
    context = {}

    client = get_catalogue_client()
    filter_value = [MultiSelectFilter("urn",id )]
    search_results = client.search(query="", page=None, filters=filter_value)
    context["result"] = search_results.page_results[0]
   
    return render(request, "details.html", context)

def search_view(request):
    
    query = request.GET.get("query", "")
    page = request.GET.get("page", None)

    client = get_catalogue_client()
    
    search_results = client.search(query=query, page=page)
    context = {}
    domain_list=search_results.facets['domains']
    context["domainlist"]=domain_list
 
    if request.GET.getlist("domain"):
        domains=request.GET.getlist("domain")
        selected_domain={}
       
        for domain in domain_list:
            if domain.value in domains:
                selected_domain[domain.value]=domain.label
       
        context['selected_domain'] = selected_domain
        
        filter_value = [MultiSelectFilter("domains",domains )]

    elif request.GET.get('clear_filter') == "True": 
        print("clear_filter")
        filter_value =[]
        context['selected_domain'] ={}
    elif request.GET.get('clear_label'): 
            print("clear label")
            filter_value =[]
            label_value=request.GET.getlist("value")
            print(label_value)
    else: 
        filter_value =[]
        context['selected_domain'] ={}
      
    
    search_results = client.search(query=query, page=page, filters=filter_value)
   

    context["query"] = query
    context["results"] = search_results.page_results
    context["total_results"] = search_results.total_results
 
    return render(request, "search.html", context)
   