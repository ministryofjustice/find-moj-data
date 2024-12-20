from typing import Any

from django.conf import settings


def env(request) -> dict[str, Any]:
    return {"ENV": settings.ENV}


def analytics(request) -> dict[str, Any]:
    return {
        "ENABLE_ANALYTICS": settings.ENABLE_ANALYTICS,
        "ANALYTICS_ID": settings.ANALYTICS_ID,
        "GIT_REF": settings.GIT_REF,
    }


def notify_enabled(request) -> dict[str, Any]:
    return {"NOTIFY_ENABLED": settings.NOTIFY_ENABLED}
