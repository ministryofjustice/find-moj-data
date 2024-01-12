from django.conf import settings
from django.shortcuts import render


# Create your views here.
def home_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    return render(request, "home.html", context)


def search_view(request):
    context = {}
    context["service_name"] = "Daap Data Catalogue"
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render(request, "search.html", context)
