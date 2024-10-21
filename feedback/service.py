import logging

from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient

from feedback.models import ReportIssue

log = logging.getLogger(__name__)

notifications_client: NotificationsAPIClient = NotificationsAPIClient(
    settings.NOTIFY_API_KEY
)


def send_notifications(issue: ReportIssue) -> None:

    personalisation = {
        "assetOwner": (
            issue.data_owner_email if issue.data_owner_email else "Data Catalog Team"
        ),
        "userEmail": issue.user_email,
        "assetName": issue.entity_name,
        "userMessage": issue.additional_info,
        "assetUrl": issue.entity_url,
    }

    reference = str(issue.id)

    # Notify Data Owner
    if issue.data_owner_email:
        notify(
            personalisation=personalisation,
            template_id=settings.NOTIFY_DATA_OWNER_TEMPLATE_ID,
            email_address=issue.data_owner_email,
            reference=reference,
        )

    # Notify Sender
    if issue.user_email:
        notify(
            personalisation=personalisation,
            template_id=settings.NOTIFY_SENDER_TEMPLATE_ID,
            email_address=issue.user_email,
            reference=reference,
        )

    # Notify Data Catalog
    notify(
        personalisation=personalisation,
        template_id=settings.NOTIFY_DATA_CATALOGUE_TEMPLATE_ID,
        email_address=settings.DATA_CATALOGUE_EMAIL,
        reference=reference,
    )


def notify(
    personalisation: dict[str, str],
    template_id: str,
    email_address: str,
    reference: str,
) -> None:

    try:
        response = notifications_client.send_email_notification(
            email_address=email_address,  # required string
            template_id=template_id,  # required UUID string
            personalisation=personalisation,
            reference=reference,
        )
    except Exception as e:
        log.exception(e)
    else:
        log.info(response)
