import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestFeedbackView:
    def test_form_renders(self, client):
        response = client.get(reverse("feedback:feedback"), data={})
        assert response.status_code == 200

    def test_invalid_form_renders(self, client):
        response = client.post(reverse("feedback:feedback"), data={})
        assert response.status_code == 200

    def test_valid_form_redirects(self, client):
        response = client.post(
            reverse("feedback:feedback"), data={"satisfaction_rating": 5}
        )
        assert response.status_code == 302
        assert response.url == reverse("feedback:thanks")

    def test_thankyou_renders(self, client):
        response = client.get(reverse("feedback:thanks"), data={})
        assert response.status_code == 200


@pytest.mark.django_db
class TestReportIssueView:
    def test_form_renders(self, client):
        response = client.get(
            reverse("feedback:report-issue"),
            data={
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
                "data_owner_email": "data.owner@justice.gov.uk",
            },
        )
        assert response.status_code == 200

    def test_invalid_form_renders(self, client):
        response = client.get(
            reverse("feedback:report-issue"),
            data={
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
            },
        )
        assert response.status_code == 200
        response = client.post(
            reverse("feedback:report-issue"),
            data={
                "reason": "Other",
                "additional_info": "a" * 9,
            },
        )
        assert response.status_code == 200

    def test_valid_form_redirects(self, client, mock_notify_service):
        response = client.get(
            reverse("feedback:report-issue"),
            data={
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
            },
        )
        assert response.status_code == 200
        response = client.post(
            reverse("feedback:report-issue"),
            data={
                "reason": "Other",
                "additional_info": "This is some additional information.",
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("feedback:thanks")
