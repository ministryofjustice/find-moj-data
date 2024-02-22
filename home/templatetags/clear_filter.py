from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    print(key)
    print(dictionary)
    return dictionary.get(key)


@register.filter
def get_items(dictionary, key):
    return dictionary.get(key).items()
