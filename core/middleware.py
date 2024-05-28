import logging

from data_platform_catalogue.client.exceptions import ConnectivityError
from django.shortcuts import render

logger = logging.getLogger(__name__)


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, ConnectivityError):
            logger.exception(exception)
            return render(request, "500_datahub_unavailable.html", status=500)
