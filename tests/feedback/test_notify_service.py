import csv

import pytest
from django.forms.models import model_to_dict
from notifications_python_client import prepare_upload

from feedback.forms import (
    FeedbackNoForm,
    FeedbackReportForm,
    FeedbackYesForm,
)
from feedback.models import FeedBackNo, FeedBackReport, FeedBackYes, Issue
from feedback.service import send, send_feedback_notification


@pytest.mark.django_db
def test_send_all_notifications(mock_notifications_client, reporter):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "data_custodian_email": "entity_owner@justice.gov.uk",
        "created_by": reporter,
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client, send_email_to_reporter=True)

    assert mock_notifications_client.send_email_notification.call_count == 3


@pytest.mark.django_db
def test_send_notifications_no_data_custodian_email(
    mock_notifications_client, reporter
):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "created_by": reporter,
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client, send_email_to_reporter=True)

    assert mock_notifications_client.send_email_notification.call_count == 2


@pytest.mark.django_db
def test_send_all_notifications_no_reporter(mock_notifications_client):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "data_custodian_email": "entity_owner@justice.gov.uk",
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client, send_email_to_reporter=False)
    assert mock_notifications_client.send_email_notification.call_count == 2


@pytest.mark.django_db
def test_send_all_notifications_no_reporter_no_data_custodian_email(
    mock_notifications_client, reporter
):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "created_by": reporter,
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client, send_email_to_reporter=False)

    assert mock_notifications_client.send_email_notification.call_count == 1


@pytest.mark.django_db
def test_entity_url_encoding(reporter):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost:8000/details/table/urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.derived_oasys_dim.dim_ref_question,PROD)",  # noqa: E501
        "created_by": reporter,
    }

    encoded_entity_url = "http://localhost:8000/details/table/urn%3Ali%3Adataset%3A%28urn%3Ali%3AdataPlatform%3Adbt%2Ccadet.awsdatacatalog.derived_oasys_dim.dim_ref_question%2CPROD%29"  # noqa: E501

    issue = Issue.objects.create(**data)
    assert issue
    assert issue.encoded_entity_url == encoded_entity_url


@pytest.mark.django_db
def test_send_yes_feedback_notification_settings(mock_notifications_client, settings):
    settings.NOTIFY_ENABLED = True
    settings.DATA_CATALOGUE_EMAIL = "team@foo.com"
    settings.NOTIFY_FEEDBACK_TEMPLATE_ID = "abc"
    form = FeedbackYesForm(
        {
            "easy_to_find": True,
            "url_path": "/some-path/",
            "created_by": "newuser@justice.gov.uk",
        }
    )
    feedback: FeedBackYes = form.save()
    feedback_instance_data: dict = model_to_dict(feedback)
    filename: str = f"/tmp/{feedback.id}.csv"
    subject: str = "Is this page useful - Yes"

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=feedback_instance_data.keys(),
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerow(feedback_instance_data)

    with open(filename, "rb") as f:
        personalisation = {
            "subject": subject,
            "userEmail": (feedback.created_by_email),
            "link_to_file": prepare_upload(
                f, filename="feedback.csv", confirm_email_before_download=False
            ),
        }

    send_feedback_notification(feedback, subject)

    mock_notifications_client.send_email_notification.assert_called_once_with(
        email_address="team@foo.com",
        template_id="abc",
        personalisation=personalisation,
        reference=str(feedback.id),
    )


@pytest.mark.django_db
def test_send_no_feedback_notification_settings(mock_notifications_client, settings):
    settings.NOTIFY_ENABLED = True
    settings.DATA_CATALOGUE_EMAIL = "team@foo.com"
    settings.NOTIFY_FEEDBACK_TEMPLATE_ID = "abc"
    form = FeedbackNoForm(
        {
            "not_clear": True,
            "url_path": "/some-path/",
            "created_by": "newuser@justice.gov.uk",
        }
    )
    feedback: FeedBackNo = form.save()
    feedback_instance_data: dict = model_to_dict(feedback)
    filename: str = f"/tmp/{feedback.id}.csv"
    subject: str = "Is this page useful - No"

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=feedback_instance_data.keys(),
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerow(feedback_instance_data)

    with open(filename, "rb") as f:
        personalisation = {
            "subject": subject,
            "userEmail": (feedback.created_by_email),
            "link_to_file": prepare_upload(
                f, filename="feedback.csv", confirm_email_before_download=False
            ),
        }

    send_feedback_notification(feedback, subject)

    mock_notifications_client.send_email_notification.assert_called_once_with(
        email_address="team@foo.com",
        template_id="abc",
        personalisation=personalisation,
        reference=str(feedback.id),
    )


@pytest.mark.django_db
def test_send_report_feedback_notification_settings(
    mock_notifications_client, settings
):
    settings.NOTIFY_ENABLED = True
    settings.DATA_CATALOGUE_EMAIL = "team@foo.com"
    settings.NOTIFY_FEEDBACK_TEMPLATE_ID = "abc"
    form = FeedbackReportForm(
        {
            "not_working": True,
            "url_path": "/some-path/",
            "created_by": "newuser@justice.gov.uk",
        }
    )
    feedback: FeedBackReport = form.save()
    feedback_instance_data: dict = model_to_dict(feedback)
    filename: str = f"/tmp/{feedback.id}.csv"
    subject: str = "Report an issue with this page"

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=feedback_instance_data.keys(),
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerow(feedback_instance_data)

    with open(filename, "rb") as f:
        personalisation = {
            "subject": subject,
            "userEmail": (feedback.created_by_email),
            "link_to_file": prepare_upload(
                f, filename="feedback.csv", confirm_email_before_download=False
            ),
        }

    send_feedback_notification(feedback, subject)

    mock_notifications_client.send_email_notification.assert_called_once_with(
        email_address="team@foo.com",
        template_id="abc",
        personalisation=personalisation,
        reference=str(feedback.id),
    )
