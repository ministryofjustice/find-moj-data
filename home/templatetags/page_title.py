from django import template
from django.conf import settings

register = template.Library()


@register.filter
def render_title(h1_value: str) -> str:
    """Renders a compliant page title for  based on the h1 value,
    service name and gov uk suffix."""
    return f"{h1_value} - {settings.SERVICE_NAME} - {settings.GOV_UK_SUFFIX}"
