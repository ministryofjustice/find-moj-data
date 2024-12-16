import logging
import threading

from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient

from feedback.models import Issue

log = logging.getLogger(__name__)


def get_notify_api_client() -> NotificationsAPIClient:
    return NotificationsAPIClient(settings.NOTIFY_API_KEY)


def send_notifications(issue: Issue, send_email_to_reporter: bool) -> None:
    if settings.NOTIFY_ENABLED:
        client = get_notify_api_client()
        # Spawn a thread to process the sending of notifcations and avoid potential delays
        # returning a response to the user.
        t = threading.Thread(target=send, args=(issue, client, send_email_to_reporter))
        t.start()


def send(
    issue: Issue, client: NotificationsAPIClient, send_email_to_reporter: bool
) -> None:

    personalisation = {
        "assetOwner": (
            issue.data_custodian_email
            if issue.data_custodian_email
            else "Data Catalog Team"
        ),
        "userEmail": issue.created_by.email if issue.created_by else "",
        "assetName": issue.entity_name,
        "userMessage": issue.additional_info,
        "assetUrl": issue.encoded_entity_url,
    }

    reference = str(issue.id)

    # Notify Data Owner
    if issue.data_custodian_email:
        notify(
            personalisation=personalisation,
            template_id=settings.NOTIFY_DATA_OWNER_TEMPLATE_ID,
            email_address=issue.data_custodian_email,
            reference=reference,
            client=client,
        )

    # Notify Sender
    if issue.created_by and send_email_to_reporter:
        notify(
            personalisation=personalisation,
            template_id=settings.NOTIFY_SENDER_TEMPLATE_ID,
            email_address=issue.created_by.email,
            reference=reference,
            client=client,
        )

    # Notify Data Catalog
    notify(
        personalisation=personalisation,
        template_id=settings.NOTIFY_DATA_CATALOGUE_TEMPLATE_ID,
        email_address=settings.DATA_CATALOGUE_EMAIL,
        reference=reference,
        client=client,
    )


def notify(
    personalisation: dict[str, str],
    template_id: str,
    email_address: str,
    reference: str,
    client: NotificationsAPIClient,
) -> None:

    try:
        response = client.send_email_notification(
            email_address=email_address,  # required string
            template_id=template_id,  # required UUID string
            personalisation=personalisation,
            reference=reference,
        )
    except Exception as e:
        log.exception(e)
    else:
        log.info(response)
