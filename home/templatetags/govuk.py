from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("partial/govuk/pagination.html")
def pagination(page_obj, urlpattern, **url_kwargs):
    paginator = page_obj.paginator
    context = {"page_obj": page_obj, "paginator": paginator}

    if page_obj.has_previous():
        context["prev_page"] = {
            "url": reverse(
                urlpattern,
                kwargs=dict(page=page_obj.previous_page_number(), **url_kwargs),
            )
        }
    if page_obj.has_next():
        context["next_page"] = {
            "url": reverse(
                urlpattern, kwargs=dict(page=page_obj.next_page_number(), **url_kwargs)
            )
        }

    numbers = []
    for page_number in paginator.get_elided_page_range(  # type: ignore
        page_obj.number, on_each_side=2, on_ends=1
    ):
        if page_number == paginator.ELLIPSIS:
            numbers.append({"is_ellipses": True})
        else:
            numbers.append(
                {
                    "number": page_number,
                    "url": reverse(
                        urlpattern, kwargs=dict(page=page_number, **url_kwargs)
                    ),
                }
            )

    context["page_numbers"] = numbers

    return context


@register.filter(name="quality_tag")
def quality_tag(value: str):
    """Map quality values to GOV.UK tag colors"""
    mapping = {"poor": "red", "acceptable": "yellow", "good": "green"}
    return mapping.get(value.lower(), "grey")  # Default to grey if value is unknown
