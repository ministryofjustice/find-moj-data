from django import template
from django.conf import settings

register = template.Library()


@register.filter
def render_title(h1_value: str = None) -> str:
    """Renders a compliant page title for  based on the h1 value,
    service name and gov uk suffix."""
    title = [h1_value] if h1_value else []
    title = title + [settings.SERVICE_NAME, settings.GOV_UK_SUFFIX]
    return " - ".join(title)
