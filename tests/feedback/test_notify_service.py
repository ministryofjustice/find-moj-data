import pytest

from feedback.models import Issue
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
def test_send_feedback_notification(mock_notifications_client, settings):
    settings.NOTIFY_ENABLED = True
    settings.DATA_CATALOGUE_EMAIL = "team@foo.com"
    settings.NOTIFY_FEEDBACK_TEMPLATE_ID = "abc"

    send_feedback_notification(
        user_email="foo@bar.com",
        satisfaction_rating="ok",
        how_can_we_improve="more data",
    )

    mock_notifications_client.send_email_notification.assert_called_once_with(
        email_address="team@foo.com",
        template_id="abc",
        personalisation={
            "userEmail": "foo@bar.com",
            "satisfactionRating": "ok",
            "howCanWeImprove": "more data",
        },
        reference=None,
    )
