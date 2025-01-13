from unittest.mock import MagicMock

from django.core.exceptions import BadRequest
from django.http import Http404

from core.middleware import CustomErrorMiddleware
from datahub_client.client.exceptions import ConnectivityError


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


def test_middleware_renders_http404_response():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = Http404()
    response = middleware.process_exception(request, error)

    assert response
    assert b"Asset does not exist" in response.content
    assert response.status_code == 404


def test_middleware_renders_unhandled_exception_response():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = Exception()
    response = middleware.process_exception(request, error)

    assert response
    assert b"There is a problem with this service" in response.content
    assert response.status_code == 500
