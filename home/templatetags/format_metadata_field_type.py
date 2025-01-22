from django import template

register = template.Library()


@register.filter
def format_metadata_field_type(value: dict) -> str:
    output = ""
    if value.get("title"):
        if value.get("type"):
            type_string = value["type"]
        if value.get("anyOf"):
            type_string = " or ".join(item["type"] for item in value["anyOf"])
        output = type_string
    elif value.get("allOf") or value.get("$ref"):
        output = "object"
    return output
