import pytest

from home.templatetags.clear_filter import format_label


@pytest.mark.parametrize(
    "label, expected", [("electronic_monitoring", "Electronic monitoring")]
)
def test_format_label(label, expected):
    assert format_label(label) == expected
