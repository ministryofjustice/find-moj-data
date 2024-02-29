from django import template
from django.utils.itercompat import is_iterable

register = template.Library()


# Backport from unreleased Django
# This can be removed after Django 5.1 is released
@register.simple_tag(takes_context=True)
def query_string(context, query_dict=None, **kwargs):
    """
    Add, remove, and change parameters of a ``QueryDict`` and return the result
    as a query string. If the ``query_dict`` argument is not provided, default
    to ``request.GET``.
    For example::
        {% query_string foo=3 %}
    To remove a key::
        {% query_string foo=None %}
    To use with pagination::
        {% query_string page=page_obj.next_page_number %}
    A custom ``QueryDict`` can also be used::
        {% query_string my_query_dict foo=3 %}
    """
    if query_dict is None:
        query_dict = context.request.GET
    query_dict = query_dict.copy()
    for key, value in kwargs.items():
        if value is None:
            if key in query_dict:
                del query_dict[key]
        elif is_iterable(value) and not isinstance(value, str):
            query_dict.setlist(key, value)
        else:
            query_dict[key] = value
    if not query_dict:
        return ""
    query_string = query_dict.urlencode()
    return f"?{query_string}"
