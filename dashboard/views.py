from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import render

from .service import generate_embed_url_for_anonymous_user


def metadata_quality_dashboard(request) -> HttpResponse:
    quicksight_embedded_url = generate_embed_url_for_anonymous_user()
    if not quicksight_embedded_url:
        raise BadRequest("Error generating QuickSight embedded URL")
    else:
        return render(
            request,
            "dashboard.html",
            {
                "h1_value": "Metadata quality dashboard",
                "dashboard_url": quicksight_embedded_url,
            },
        )
