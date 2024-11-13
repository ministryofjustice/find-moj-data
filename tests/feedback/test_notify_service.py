import pytest

from feedback.models import Issue
from feedback.service import send


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
def test_send_notifications_no_data_custodian_email(mock_notifications_client, reporter):
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
