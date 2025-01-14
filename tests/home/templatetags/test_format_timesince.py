import pytest

from home.templatetags.format_timesince import format_timesince


@pytest.mark.parametrize(
    "timesince, expected_result",
    [
        ("30 seconds", "30 seconds"),
        ("1 hour, 45 minutes", "1 hour"),
        ("1 day, 6 hours, 45 minutes", "1 day"),
    ],
)
def test_format_timesince(timesince, expected_result):
    assert format_timesince(timesince) == expected_result
