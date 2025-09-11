from html import escape

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestFeedbackView:
    def test_feedback_yes_form_renders(self, client):
        response = client.get(reverse("feedback:yes"), data={})
        assert response.status_code == 200

    def test_feedback_no_form_renders(self, client):
        response = client.post(reverse("feedback:no"), data={})
        assert response.status_code == 200

    def test_feedback_report_form_renders(self, client):
        response = client.post(reverse("feedback:report"), data={})
        assert response.status_code == 200

    def test_valid_yes_form_redirects(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={"url_path": "/some/path", "easy_to_find": True},
        )
        subject = "We'll use it to improve the service."
        assert response.status_code == 200
        assert escape(subject) in response.text

    def test_invalid_yes_form_renders_error(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={"easy_to_find": True},
        )
        error = "There is a problem"
        assert response.status_code == 200
        assert error in response.text

    def test_valid_no_form_redirects(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={"url_path": "/some/path", "not_clear": True},
        )
        subject = "We'll use it to improve the service."
        assert response.status_code == 200
        assert escape(subject) in response.text

    def test_invalid_no_form_renders_error(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={"not_clear": True},
        )
        error = "There is a problem"
        assert response.status_code == 200
        assert error in response.text

    def test_valid_report_form_redirects(self, client):
        response = client.post(
            reverse("feedback:report"),
            data={
                "url_path": "/some/path",
                "not_working": True,
            },
        )
        subject = "We look at every report received."
        assert response.status_code == 200
        assert escape(subject) in response.text

    def test_invalid_report_form_renders_error(self, client):
        response = client.post(
            reverse("feedback:report"),
            data={
                "not_working": True,
            },
        )
        error = "There is a problem"
        assert response.status_code == 200
        assert error in response.text


@pytest.mark.django_db
class TestReportIssueView:
    @pytest.fixture(autouse=True)
    def setup_user(self, reporter, client):
        client.force_login(reporter)

    def test_form_renders(self, client):
        response = client.get(
            reverse("feedback:report-issue"),
            data={
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
                "data_custodian_email": "data.owner@justice.gov.uk",
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

    def test_valid_form_redirects(self, client):
        response = client.get(
            reverse("feedback:report-issue"),
            data={
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
                "data_custodian_email": "data.owner@justice.gov.uk",
            },
        )
        assert response.status_code == 200
        response = client.post(
            reverse("feedback:report-issue"),
            data={
                "reason": "Other",
                "additional_info": "This is some additional information.",
                "entity_name": "my_entity",
                "entity_url": "http://localhost/my_entity",
                "data_custodian_email": "data.owner@justice.gov.uk",
                "send_email_to_reporter": "Yes",
            },
        )
        assert response.status_code == 302
        assert response.url == "http://localhost/my_entity"
