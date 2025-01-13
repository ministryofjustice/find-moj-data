from datahub_client.search_types import SortOption


def test_format_sort_option():
    expected = {
        "sortCriterion": {
            "field": "test",
            "sortOrder": "DESCENDING",
        }
    }
    result = SortOption(field="test", ascending=False)

    assert result.format() == expected
