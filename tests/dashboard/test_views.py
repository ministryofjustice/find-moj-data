from unittest import mock

import pytest
from django.core.exceptions import BadRequest
from django.test import RequestFactory

from dashboard.views import metadata_quality_dashboard


@pytest.fixture
def rf():
    return RequestFactory()


@mock.patch("dashboard.views.generate_embed_url_for_anonymous_user")
def test_metadata_quality_dashboard_success(mock_generate_url, rf):
    mock_generate_url.return_value = "http://example.com"
    request = rf.get("/dashboard/")
    response = metadata_quality_dashboard(request)

    assert response.status_code == 200
    assert "Metadata quality dashboard" in response.content.decode()
    assert "http://example.com" in response.content.decode()


@mock.patch("dashboard.views.generate_embed_url_for_anonymous_user")
def test_metadata_quality_dashboard_failure(mock_generate_url, rf):
    mock_generate_url.return_value = None
    request = rf.get("/dashboard/")
    with pytest.raises(BadRequest) as excinfo:
        metadata_quality_dashboard(request)
    assert str(excinfo.value) == "Error generating QuickSight embedded URL"
