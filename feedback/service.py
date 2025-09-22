import csv
import logging
import threading

from django.conf import settings
from django.forms.models import model_to_dict
from notifications_python_client import prepare_upload
from notifications_python_client.notifications import NotificationsAPIClient

from feedback.models import FeedBackNo, FeedBackReport, FeedBackYes, Issue

log = logging.getLogger(__name__)


def get_notify_api_client() -> NotificationsAPIClient:
    return NotificationsAPIClient(settings.NOTIFY_API_KEY)


def send_feedback_notification(
    feedback_instance: FeedBackYes | FeedBackNo | FeedBackReport,
    subject: str,
) -> None:
    if settings.NOTIFY_ENABLED:
        client: NotificationsAPIClient = get_notify_api_client()
        feedback_instance_data: dict = model_to_dict(feedback_instance)
        filename: str = f"/tmp/{feedback_instance.id}.csv"

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
                "userEmail": (feedback_instance.created_by_email),
                "link_to_file": prepare_upload(
                    f, filename="feedback.csv", confirm_email_before_download=False
                ),
            }

            t = threading.Thread(
                target=notify,
                kwargs={
                    "personalisation": personalisation,
                    "template_id": settings.NOTIFY_FEEDBACK_TEMPLATE_ID,
                    "email_address": settings.DATA_CATALOGUE_EMAIL,
                    "client": client,
                    "reference": str(feedback_instance.id),
                },
            )
            t.start()


def send_issue_notifications(issue: Issue, send_email_to_reporter: bool) -> None:
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
            template_id=settings.NOTIFY_DATA_CATALOGUE_OR_DATA_OWNER_TEMPLATE_ID,
            email_address=issue.data_custodian_email,
            reference=reference,
            client=client,
        )

    # Notify Reporter
    if issue.created_by and send_email_to_reporter:
        if issue.data_custodian_email:
            reporter_template_id = (
                settings.NOTIFY_REPORTER_INCLUDING_DATA_CATALOGUE_AND_DATA_OWNER_TEMPLATE_ID  # noqa E501
            )
            personalisation.update({"assetOwner": issue.data_custodian_email})

        else:
            reporter_template_id = (
                settings.NOTIFY_REPORTER_DATA_CATALOGUE_ONLY_TEMPLATE_ID
            )

        notify(
            personalisation=personalisation,
            template_id=reporter_template_id,
            email_address=issue.created_by.email,
            reference=reference,
            client=client,
        )

    # Notify Data Catalog
    notify(
        personalisation=personalisation,
        template_id=settings.NOTIFY_DATA_CATALOGUE_OR_DATA_OWNER_TEMPLATE_ID,
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
