from unittest.mock import MagicMock

from data_platform_catalogue.client.exceptions import ConnectivityError
from django.core.exceptions import BadRequest
from django.http import Http404

from core.middleware import CustomErrorMiddleware


def test_middleware_renders_connectivity_response():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = ConnectivityError()
    response = middleware.process_exception(request, error)

    assert response
    assert b"Catalogue service unavailable" in response.content
    assert response.status_code == 500


def test_middleware_renders_bad_request_response():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = BadRequest()
    response = middleware.process_exception(request, error)

    assert response
    assert b"Bad request" in response.content
    assert response.status_code == 400


def test_middleware_renders_unhandled_exception_response():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = Exception()
    response = middleware.process_exception(request, error)

    assert response
    assert b"Server error" in response.content
    assert response.status_code == 500
