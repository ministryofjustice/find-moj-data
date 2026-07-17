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
            data={"url_path": "/some/path", "easy_to_find": True, "interested_in_research": True},
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

    def test_invalid_yes_form_targets_research_radios_with_inline_error(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={"easy_to_find": True, "url_path": "/some/path"},
        )
        assert response.status_code == 200
        assert 'id="id_interested_in_research"' in response.text
        assert 'class="govuk-form-group govuk-form-group--error"' in response.text
        assert 'id="id_interested_in_research-error" class="govuk-error-message"' in response.text
        assert "Choose Yes or No to submit" in response.text

    def test_yes_form_requires_what_went_well_when_something_else_checked(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={
                "url_path": "/some/path",
                "something_else": True,
                "interested_in_research": True,
            },
        )
        assert response.status_code == 200
        assert "Tell us what went well to continue" in response.text
        assert "govuk-checkboxes__conditional--error" in response.text

    def test_yes_form_accepts_something_else_with_text(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={
                "url_path": "/some/path",
                "something_else": True,
                "what_went_well": "Found exactly what I needed",
                "interested_in_research": True,
            },
        )
        assert response.status_code == 200
        assert escape("We'll use it to improve the service.") in response.text

    def test_yes_form_rejects_only_optional_additional_information(self, client):
        response = client.post(
            reverse("feedback:yes"),
            data={
                "url_path": "/some/path",
                "additional_information": "Some optional notes",
                "interested_in_research": True,
            },
        )
        assert response.status_code == 200
        assert "Select one or more options to continue" in response.text

    def test_valid_no_form_redirects(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={"url_path": "/some/path", "not_clear": True, "interested_in_research": False},
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

    def test_invalid_no_form_targets_research_radios_with_inline_error(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={"not_clear": True, "url_path": "/some/path"},
        )
        assert response.status_code == 200
        assert 'id="id_interested_in_research"' in response.text
        assert 'class="govuk-form-group govuk-form-group--error"' in response.text
        assert 'id="id_interested_in_research-error" class="govuk-error-message"' in response.text
        assert "Choose Yes or No to submit" in response.text

    def test_no_form_accepts_something_else_with_text(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={
                "url_path": "/some/path",
                "something_else": True,
                "what_went_wrong": "Could not locate governance details",
                "interested_in_research": False,
            },
        )
        assert response.status_code == 200
        assert escape("We'll use it to improve the service.") in response.text

    def test_no_form_rejects_only_optional_additional_information(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={
                "url_path": "/some/path",
                "additional_information": "Some optional notes",
                "interested_in_research": False,
            },
        )
        assert response.status_code == 200
        assert "Select one or more options to continue" in response.text

    def test_no_form_requires_what_went_wrong_when_something_else_checked(self, client):
        response = client.post(
            reverse("feedback:no"),
            data={
                "url_path": "/some/path",
                "something_else": True,
                "interested_in_research": False,
            },
        )
        assert response.status_code == 200
        assert "Tell us what was wrong to continue" in response.text

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

    def test_report_form_requires_some_other_issue_when_something_else_checked(self, client):
        response = client.post(
            reverse("feedback:report"),
            data={
                "url_path": "/some/path",
                "something_else": True,
            },
        )
        assert response.status_code == 200
        assert "Tell us what was wrong to continue" in response.text
        assert "govuk-checkboxes__conditional--error" in response.text


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
