import json
import os
from typing import Any

from django.http import Http404
from sentry_sdk.types import Event, Hint


def generate_cache_configuration() -> dict[str, Any]:
    """
    Generates appropriate cache configuration for the given environment
    """
    cache = {}
    cache["BACKEND"] = "django.core.cache.backends.locmem.LocMemCache"

    # Utilising Redis in Non local development environments
    if (
        os.environ.get("REDIS_AUTH_TOKEN")
        and os.environ.get("REDIS_PRIMARY_ENDPOINT_ADDRESS")
        and os.environ.get("REDIS_MEMBER_CLUSTERS")
    ):
        REDIS_DB_VALUE: int = 0
        cache["BACKEND"] = "django.core.cache.backends.redis.RedisCache"

        location: list[str] = []
        location.append(
            f"rediss://:{os.environ.get('REDIS_AUTH_TOKEN')}@{os.environ.get('REDIS_PRIMARY_ENDPOINT_ADDRESS')}/{REDIS_DB_VALUE}"  # noqa: E501
        )

        domain: str = ".".join(
            os.environ.get("REDIS_PRIMARY_ENDPOINT_ADDRESS", "").split(".")[1:]
        )  # 'cpf05ff2dca7d81952.iwfvzo.euw2.cache.amazonaws.com'

        hosts: list[str] = json.loads(
            os.environ.get("REDIS_MEMBER_CLUSTERS", [])
        )  # ["cp-f05ff2dca7d81952-001","cp-f05ff2dca7d81952-002"]

        for host in hosts:
            location.append(
                f"rediss://:{os.environ.get('REDIS_AUTH_TOKEN')}@{host}.{domain}/{REDIS_DB_VALUE}"  # noqa: E501
            )

        cache["LOCATION"] = location

    return {"default": cache}


def before_send(event: Event, hint: Hint) -> Event | None:
    """Helper function to inspect and filter errors before they are sent to Sentry.
    In this case, we are filtering out Http404 errors that are raised when a requested
    entity does not exist.

    Args:
        event (Event): Sentry event
        hint (Hint): Sentry hint containing exception information

    Returns:
        Event | None: Returns the event if it is not an Http404 error, otherwise None
    """
    exception_messages_404 = ["Asset does not exist", "Page not found"]
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        # Check if the exception is an Http404 error
        if isinstance(exc_value, Http404):
            # Check if we have a known error message string that we want to filter out
            for message in exception_messages_404:
                if message in str(exc_value.args[0]):
                    return None
    return event
