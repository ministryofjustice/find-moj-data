from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeText, mark_safe
from markdown import markdown as markdown_func

register = template.Library()


@register.filter
@stringfilter
def markdown(value, heading_offset=0) -> SafeText:
    return mark_safe(
        """
        <div class="markdown-container">
        """
        + markdown_func(
            value,
            extensions=["fenced_code", "mdx_headdown", "sane_lists"],
            extension_configs={
                "mdx_headdown": {"offset": heading_offset},
            },
        )
        + """
        </div>
        """
    )
