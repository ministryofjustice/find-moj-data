import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def get_quicksight_client():
    sts = boto3.client("sts")
    role_response = sts.assume_role(
        RoleArn=settings.QUICKSIGHT_ROLE_ARN, RoleSessionName="quicksight"
    )["Credentials"]

    session = boto3.Session(
        aws_access_key_id=role_response["AccessKeyId"],
        aws_secret_access_key=role_response["SecretAccessKey"],
        aws_session_token=role_response["SessionToken"],
    )

    return session.client("quicksight")


def generate_embed_url_for_anonymous_user() -> str | None:
    """
    Generates an embed URL for an anonymous user to access a QuickSight dashboard.

    Returns:
        str | None: The embed URL if successful, otherwise None.
    """
    quicksight_client = get_quicksight_client()
    try:
        response = quicksight_client.generate_embed_url_for_anonymous_user(
            AwsAccountId=settings.QUICKSIGHT_ACCOUNT_ID,
            Namespace=settings.QUICKSIGHT_NAMESPACE,
            AuthorizedResourceArns=[settings.QUICKSIGHT_METADATA_DASHBOARD_ARN],
            ExperienceConfiguration={
                "Dashboard": {
                    "InitialDashboardId": settings.QUICKSIGHT_METADATA_DASHBOARD_ID
                }
            },
            SessionLifetimeInMinutes=600,
        )

        return response["EmbedUrl"]

    except ClientError as e:
        logging.error(
            f"Failed to generate embed URL for anonymous user: {e.response['Error']['Message']}"
        )
        return None
