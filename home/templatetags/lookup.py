from home.templatetags.markdown import register


@register.filter
def lookup(list, lookup_dict):
    return sorted([lookup_dict.get(item) for item in list])
