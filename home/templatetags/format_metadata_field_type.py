from django import template

register = template.Library()


@register.filter
def format_metadata_field_type(value: dict) -> dict[str, str]:
    if value.get("title"):
        title = value["title"].lower().replace(" ", "_")
        if value.get("type"):
            type_string = value["type"]
        if value.get("anyOf"):
            type_string = " or ".join(item["type"] for item in value["anyOf"])
        output = {"field_name": title, "field_type": type_string}
    if value.get("allOf"):
        linked_entity = value["allOf"][0]["$ref"].split("/")[2]
        output = {"field_name": linked_entity, "field_type": "object"}
    return output
