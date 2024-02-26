from django import template

register = template.Library()


@register.filter
def get_item(dictionary: dict[str, dict], key: str) -> dict[str, list | str]:
    return dictionary.get(key)


@register.filter
def get_items(dictionary: dict[str, dict], key: str) -> list:
    return dictionary.get(key).items()


@register.filter
def get_keys(dictionary: dict[str, dict]) -> list[str] | list:
    if dictionary:
        return dictionary.keys()
    return []


@register.filter
def format_label(label: str) -> str:
    return label.replace("_", " ").title() if "_" in label else label
