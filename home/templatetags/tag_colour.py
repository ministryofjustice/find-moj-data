from django import template

register = template.Library()


@register.filter
def tag_colour(entity: str = None) -> str:
    """Renders a compliant page title for  based on the h1 value,
    service name and gov uk suffix."""
    match entity:
        case "Database":
            return "govuk-tag--green"
        case "Table":
            return "govuk-tag--purple"
        case "Chart":
            return "govuk-tag--yellow"
        case "Schema":
            return "govuk-tag--teal"
        case "Dashboard":
            return "govuk-tag--grey"
        case "Publication collection":
            return "govuk-tag--blue"
        case "Publication dataset":
            return "govuk-tag--light-blue"
