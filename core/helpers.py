import os
from typing import Any


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

        domain = ".".join(
            os.environ.get("REDIS_PRIMARY_ENDPOINT_ADDRESS", "").split(".")[2:]
        )

        hosts: list[str] = os.environ.get(
            "REDIS_MEMBER_CLUSTERS", ""
        ).split()  # ["cp-f05ff2dca7d81952-001","cp-f05ff2dca7d81952-002"]

        for host in hosts:
            location.append(
                f"rediss://:{os.environ.get('REDIS_AUTH_TOKEN')}@{host}.{domain}/{REDIS_DB_VALUE}"  # noqa: E501
            )

        cache["LOCATION"] = location

    return {"default": cache}
