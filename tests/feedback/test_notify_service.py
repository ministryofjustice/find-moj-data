import pytest

from feedback.models import Issue
from feedback.service import send


@pytest.mark.django_db
def test_send_all_notifications(mock_notifications_client):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "data_owner_email": "entity_owner@justice.gov.uk",
        "user_email": "userx@justice.gov.uk",
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client)

    assert mock_notifications_client.send_email_notification.call_count == 3


@pytest.mark.django_db
def test_send_notifications_no_data_owner_email(mock_notifications_client):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "user_email": "userx@justice.gov.uk",
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client)

    assert mock_notifications_client.send_email_notification.call_count == 2


@pytest.mark.django_db
def test_send_all_notifications_no_user_email(mock_notifications_client):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
        "data_owner_email": "entity_owner@justice.gov.uk",
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client)

    assert mock_notifications_client.send_email_notification.call_count == 2


@pytest.mark.django_db
def test_send_all_notifications_no_user_or_data_owner_email(mock_notifications_client):
    data = {
        "reason": "Other",
        "additional_info": "This is some additional information.",
        "entity_name": "my_entity",
        "entity_url": "http://localhost/my_entity",
    }

    issue = Issue.objects.create(**data)
    assert issue

    send(issue=issue, client=mock_notifications_client)

    assert mock_notifications_client.send_email_notification.call_count == 1
