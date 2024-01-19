from django.conf import settings
from django.shortcuts import render


# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)


def search_view(request):
    context = {}
    context.update(settings.SAMPLE_SEARCH_RESULTS)
    return render(request, "search.html", context)
