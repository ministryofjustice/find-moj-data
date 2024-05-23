from itertools import dropwhile

from django.template.defaultfilters import stringfilter, truncatechars_html

from home.templatetags.markdown import register


@register.filter(is_safe=True)
@stringfilter
def truncate_snippet(value, max_chars=200):
    """
    Truncate a chunk of markup, ensuring that:

    1. At most `max_chars` characters are returned
    2. The result contains a <mark>, if possible
    3. The snippet starts at the beginning of a paragraph, if possible.
    4. Words are preserved at the start of a snippet (but they can be truncated at the end)
    5. There are no dangling HTML tags created from HTML in the text;
       Any mark tags that are opened in the string and not closed before
       the truncation point are closed immediately after the truncation.
       (Note: this can cause marked keywords to be truncated, but only if
       the keyword is already marked at an earlier point in the snippet)

    Note - this *ignores markdown syntax*, so there are edge cases where bolding
    or italics are left unterminated, in which case the formatting may be applied
    to the "…" character. It's up to the markdown parser to generate valid HTML.
    """
    end_mark_idx = value.find("</mark>")

    # Use regular truncation if there are no marks, or the mark happens within
    # the truncation limit. In this case, we don't need to truncate
    # anything from the start of the string.
    if end_mark_idx == -1 or end_mark_idx < max_chars:
        return truncatechars_html(value, arg=max_chars)

    snippet = _drop_unmarked_paragraphs(value)
    truncated_snippet = _align_snippet(snippet=snippet, max_chars=max_chars)

    return truncated_snippet


def _drop_unmarked_paragraphs(value):
    """
    Anchor the snippet at the start of a paragraph if we can do this
    without losing the marked section
    """
    paragraphs = value.replace("\r", "").split("\n\n")
    paragraphs = dropwhile(lambda p: "<mark>" not in p, paragraphs)
    return "\n\n".join(paragraphs).strip()


def _align_snippet(snippet, max_chars):
    """
    Align a snippet to a few words before start_mark_idx
    """
    start_mark_idx = snippet.find("<mark>")
    end_mark_idx = snippet[start_mark_idx + 1:].find("</mark>")

    # If the mark is at the beginning of the first remaining paragraph,
    # no further alignment is required.
    if start_mark_idx < end_mark_idx < max_chars - 1:
        return "…" + truncatechars_html(snippet, arg=max_chars - 1)

    # Split the snippet at the first <mark>
    prefix = snippet[:start_mark_idx]
    from_mark = snippet[start_mark_idx:]

    # Remove all but a few words for context
    _, *rest = prefix.rsplit(" ", maxsplit=25)
    short_prefix = " ".join(rest)
    used_length = len(short_prefix) + 1
    new_max_chars = max(max_chars - 1, used_length)

    # Anchor the snippet a few words before the mark
    return "…" + truncatechars_html(short_prefix + from_mark, arg=new_max_chars)
