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
    ],
    ids=(
        "empty string",
        "string should not be truncated",
        "string should be truncated",
        "first paragraph should be dropped",
        "beginning and end of a middle paragraph should be truncated",
    ),
)
def test_snippet(full_text, limit, expected):
    assert truncate_snippet(full_text, limit) == expected
