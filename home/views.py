from django.conf import settings
from django.shortcuts import render


def filter_json_dict(json_dict, target_value):
    filtered_dict = {key: value for key, value in json_dict.items() if value == target_value}
    return filtered_dict

# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def filter_view(request):
    data = {}
    data.update(settings.SAMPLE_SEARCH_RESULTS)

    filtered_results =[item for item in data['results'] if item['domain_name'] == 'HMPPS']
    context={'results': filtered_results, 'total': len(filtered_results)} 
   
    return render(request, "search.html", context)

def search_view(request):
    context = {}
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render(request, "search.html", context)
