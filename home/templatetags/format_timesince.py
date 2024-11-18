from home.templatetags.markdown import register


@register.filter
def format_timesince(timesince: str) -> str:
    """
    Timesince returns a string like "3 days, 4 hours". This filter will return a string like "3 days".
    """
    return timesince.split(",")[0]
