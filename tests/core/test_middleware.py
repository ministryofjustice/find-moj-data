from unittest.mock import MagicMock

from data_platform_catalogue.client.exceptions import ConnectivityError

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


def test_middleware_ignores_other_errors():
    get_response = MagicMock()
    request = MagicMock()
    middleware = CustomErrorMiddleware(get_response)
    error = Exception()
    response = middleware.process_exception(request, error)

    assert response is None
