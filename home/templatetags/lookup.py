from typing import Any

from home.templatetags.markdown import register


@register.filter
def lookup(value_list, lookup_dict) -> list[Any]:
    """
    Return a list of values by doing a dictionary lookup using elements of the input list as keys.
    Ignore any that are not in the list.
    """
    return sorted([lookup_dict[item] for item in value_list if item in lookup_dict])


@register.filter
def get_count(lookup_dict, key) -> int:
    """
    Return the count for a given key from a dictionary, defaulting to 0 if not found.
    Usage: {{ entity_type_counts|get_count:entity_type.data.value }}
    """
    if lookup_dict is None:
        return 0
    return lookup_dict.get(key, 0)
