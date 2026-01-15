import pytest

from home.templatetags.lookup import get_count, lookup


@pytest.mark.parametrize(
    "input_list, lookup_dict, output_list",
    [
        ([], {}, []),
        ([], {"foo": "bar"}, []),
        ([1, 2], {"foo": "bar"}, []),
        (["a", "b"], {"b": "c"}, ["c"]),
    ],
)
def test_lookup(input_list, lookup_dict, output_list):
    assert lookup(input_list, lookup_dict) == output_list


class TestGetCount:
    """Tests for the get_count template filter."""

    def test_get_count_returns_value_when_key_exists(self):
        lookup_dict = {"TABLE": 100, "CHART": 50}
        assert get_count(lookup_dict, "TABLE") == 100
        assert get_count(lookup_dict, "CHART") == 50

    def test_get_count_returns_zero_when_key_missing(self):
        lookup_dict = {"TABLE": 100}
        assert get_count(lookup_dict, "MISSING") == 0

    def test_get_count_returns_zero_when_dict_is_none(self):
        assert get_count(None, "TABLE") == 0

    def test_get_count_returns_zero_when_dict_is_empty(self):
        assert get_count({}, "TABLE") == 0

    def test_get_count_with_integer_keys(self):
        lookup_dict = {1: 10, 2: 20}
        assert get_count(lookup_dict, 1) == 10
        assert get_count(lookup_dict, 3) == 0
