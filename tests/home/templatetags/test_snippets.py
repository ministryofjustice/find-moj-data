import pytest

from home.templatetags.snippets import truncate_snippet


@pytest.mark.parametrize(
    "full_text, limit, expected",
    [
        ("", 200, ""),
        ("hello world", 200, "hello world"),
        ("hello world" + "!" * 200, 200, "hello world" + "!" * 188 + "…"),
        ("a" * 200 + "\n\nhello <mark>world</mark>", 200, "…hello <mark>world</mark>"),
        (
            "a" * 200 + "\n\n" + "word word word " * 100 + "hello <mark>world</mark>",
            200,
            "…word word word word word word word word word word word word word word word word word word word word word word word hello <mark>world</mark>",
        ),
        (
            "A prisoner is released in error if they are wrongly discharged from a prison or court when they should have remained in custody, where the prisoner has not deliberately played a part in the error (i.e. the prisoner had no intent of <mark>escaping</mark>).\n\nExamples include misplaced warrants for imprisonment or remand, recall notices not acted upon, sentence miscalculation or discharging the wrong person on escort.",
            300,
            "A prisoner is released in error if they are wrongly discharged from a prison or court when they should have remained in custody, where the prisoner has not deliberately played a part in the error (i.e. the prisoner had no intent of <mark>escaping</mark>).\n\nExamples include misplaced warrants for imprisonment or…",
        ),
    ],
    ids=(
        "empty string",
        "string should not be truncated",
        "string should be truncated",
        "first paragraph should be dropped",
        "beginning and end of a middle paragraph should be truncated",
        "if the snippet length is long enough, we show long paragraphs instead of short snippets",
    ),
)
def test_snippet(full_text, limit, expected):
    assert truncate_snippet(full_text, limit) == expected
