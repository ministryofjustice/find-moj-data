from django.shortcuts import render


def handler404(request, exception):
    return render(
        request,
        "404.html",
        context={"h1_value": "Page not found"},
        status=404,
    )
