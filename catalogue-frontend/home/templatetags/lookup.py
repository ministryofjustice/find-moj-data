from home.templatetags.markdown import register


@register.filter
def lookup(value_list, lookup_dict):
    return sorted([lookup_dict.get(item, "") for item in value_list])
