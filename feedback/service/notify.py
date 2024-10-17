import logging

from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient

from feedback.models import ReportIssue

log = logging.getLogger(__name__)


def send_notifications(issue: ReportIssue):
    notifications_client = NotificationsAPIClient(settings.NOTIFY_API_KEY)
    if issue.data_owner_email:
        notify_data_owner(
            issue, notifications_client, settings.NOTIFY_DATA_OWNER_TEMPLATE_ID
        )
    if issue.user_email:
        notify_sender(issue, notifications_client, settings.NOTIFY_SENDER_TEMPLATE_ID)
    notify_data_catalogue(
        issue, notifications_client, settings.NOTIFY_DATA_CATALOGUE_TEMPLATE_ID
    )


def notify_data_owner(
    issue: ReportIssue, notifications_client: NotificationsAPIClient, template_id: str
):
    try:
        response = notifications_client.send_email_notification(
            email_address=issue.data_owner_email,  # required string
            template_id=template_id,  # required UUID string
            personalisation={
                "assetOwner": issue.data_owner_email,
                "userEmail": issue.user_email,
                "assetName": issue.entity_name,
                "userMessage": issue.additional_info,
                "assetUrl": issue.entity_url,
            },
            reference=str(issue.id),
        )
    except Exception as e:
        log.exception(e)
    else:
        log.info(response)


def notify_sender(
    issue: ReportIssue, notifications_client: NotificationsAPIClient, template_id: str
):
    try:
        response = notifications_client.send_email_notification(
            email_address=issue.user_email,  # required string
            template_id=template_id,  # required UUID string
            personalisation={
                "assetOwner": issue.data_owner_email,
                "userEmail": issue.user_email,
                "assetName": issue.entity_name,
                "userMessage": issue.additional_info,
                "assetUrl": issue.entity_url,
            },
            reference=str(issue.id),
        )
    except Exception as e:
        log.exception(e)
    else:
        log.info(response)


def notify_data_catalogue(
    issue: ReportIssue, notifications_client: NotificationsAPIClient, template_id: str
):
    try:
        response = notifications_client.send_email_notification(
            email_address=issue.user_email,  # required string
            template_id=template_id,  # required UUID string
            personalisation={
                "assetOwner": "catalogueteam@digital.justice.gov.uk",
                "userEmail": issue.user_email,
                "assetName": issue.entity_name,
                "userMessage": issue.additional_info,
                "assetUrl": issue.entity_url,
            },
            reference=str(issue.id),
        )
    except Exception as e:
        log.exception(e)
    else:
        log.info(response)
