from typing import Any

from home.templatetags.markdown import register


@register.filter
def lookup(value_list, lookup_dict) -> list[Any]:
    """
    Return a list of values by doing a dictionary lookup using elements of the input list as keys.
    Ignore any that are not in the list.
    """
    return sorted([lookup_dict[item] for item in value_list if item in lookup_dict])
