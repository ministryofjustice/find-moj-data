from django.conf import settings
from django.shortcuts import render
from .services import get_catalogue_client
from data_platform_catalogue.search_types import MultiSelectFilter

def filter_seleted_domains(domain_list, domains):
    selected_domain={}
    for domain in domain_list:
        if domain.value in domains:
            selected_domain[domain.value]=domain.label
    return selected_domain
   

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

    # Fetch domainlist without query
    search_results = client.search(query="", page=None)
    context = {}
    domain_list=search_results.facets['domains']
    context["domainlist"]=domain_list
 
    if request.GET.getlist("domain"):
        domains=request.GET.getlist("domain")
        selected_domain=filter_seleted_domains(domain_list, domains)
        context['selected_domain'] = selected_domain
        request.session['selected_domain'] = selected_domain
        request.session['domains'] = domains
        filter_value = [MultiSelectFilter("domains",domains )]

    elif request.GET.get('clear_filter') == "True": 
        filter_value =[]
        context['selected_domain'] ={}
    elif request.GET.get('clear_label')=='True': 
        #Value to clear
        label_value=request.GET.getlist("value")
        
        #Remove the selected value from list
        domains=  request.session.get('domains', None)
        domains=list(set(domains) - set(label_value))
    
        #Populated selected domain
        selected_domain=filter_seleted_domains(domain_list, domains)
        context['domains'] = domains
        context['selected_domain'] = selected_domain
        
        #Reassign to session
        request.session['selected_domain'] = selected_domain
        request.session['domains'] = domains
        if not domains:
            filter_value = []
        else:
            filter_value = [MultiSelectFilter("domains",domains )]

    elif request.GET.get('query'): 
        domains=  request.session.get('domains', None)
        #Preserve filter
        selected_domain=filter_seleted_domains(domain_list, domains)
        context['selected_domain'] = selected_domain
        context['domains'] = domains
        filter_value = [MultiSelectFilter("domains",domains )]
    else: 
        filter_value =[]
        context['selected_domain'] ={}
      
    # Search with filter
    search_results = client.search(query=query, page=page, filters=filter_value)
    context["query"] = query
    context["results"] = search_results.page_results
    context["total_results"] = search_results.total_results
 
    return render(request, "search.html", context)
   