import logging

from data_platform_catalogue.client.exceptions import ConnectivityError
from django.conf import settings
from django.core.exceptions import BadRequest
from django.shortcuts import render
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception(exception)
        if settings.DEBUG:
            return
        if isinstance(exception, ConnectivityError):
            return render(
                request,
                "500_datahub_unavailable.html",
                context={"h1_value": _("Catalogue service unavailable")},
                status=500,
            )
        elif isinstance(exception, BadRequest):
            return render(
                request,
                "400.html",
                context={"h1_value": _("Bad request")},
                status=400,
            )
        elif isinstance(exception, Exception):
            return render(
                request,
                "500.html",
                context={"h1_value": _("There is a problem with this service")},
                status=500,
            )
