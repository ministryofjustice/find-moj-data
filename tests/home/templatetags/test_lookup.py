import pytest

from home.templatetags.lookup import get_readable_name, lookup


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


@pytest.mark.parametrize(
    "key, lookup_dict, expected",
    [
        ("fieldPaths", {"fieldPaths": "Column name"}, "Column name"),
        ("fieldPaths", {}, "fieldPaths"),
        ("unknown_key", {"fieldPaths": "Column name"}, "unknown_key"),
    ],
)
def test_get_item(key, lookup_dict, expected):
    assert get_readable_name(key, lookup_dict) == expected
