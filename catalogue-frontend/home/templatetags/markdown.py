from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from markdown import markdown as markdown_func

register = template.Library()


@register.filter
@stringfilter
def markdown(value):
    return mark_safe(markdown_func(value))
