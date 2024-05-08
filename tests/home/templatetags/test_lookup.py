import pytest

from home.templatetags.lookup import lookup


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
