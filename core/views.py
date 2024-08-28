from django.shortcuts import render
from django.utils.translation import gettext as _


def handler404(request, exception):
    return render(
        request,
        "404.html",
        context={"h1_value": _("Page not found")},
        status=404,
    )
