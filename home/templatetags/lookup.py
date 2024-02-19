from home.templatetags.markdown import register

@register.filter
def lookup(list, lookup_dict):
    return [lookup_dict[item] for item in list]
