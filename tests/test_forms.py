from home.forms.search import SearchForm
import pytest


@pytest.fixture
def valid_form():
    valid_form = SearchForm(
        data={
            "query": "test",
            "domains": ["urn:li:domain:HMCTS"],
            "sort": "ascending",
            "clear_filter": False,
            "clear_label": False,
        }
    )
    assert valid_form.is_valid()

    return valid_form


class TestSearchForm:
    def test_query_field_length(self):
        over_100_characters = "a" * 101
        assert not SearchForm(data={"query": over_100_characters}).is_valid()

    def test_domain_is_from_domain_list_false(self):
        assert not SearchForm(data={"domains": ["fake"]}).is_valid()

    def test_sort_is_from_sort_list_false(self):
        assert not SearchForm(data={"sort": ["fake"]}).is_valid()

    def test_all_fields_nullable(self):
        assert SearchForm(data={}).is_valid()

    def test_form_encode_without_filter_for_one_filter(self, valid_form):
        assert (valid_form.encode_without_filter("urn:li:domain:HMCTS") ==
                "?query=test&sort=ascending&clear_filter=False&clear_label=False")

    def test_form_encode_without_filter_for_two_filters(self):
        two_filter_form = SearchForm(data={
            "query": "test",
            "domains": ["urn:li:domain:HMCTS", "urn:li:domain:HMPPS"]
        })
        two_filter_form.is_valid()

        assert (two_filter_form.encode_without_filter("urn:li:domain:HMCTS") ==
                "?query=test&domains=urn%3Ali%3Adomain%3AHMPPS&sort=&clear_filter=False&clear_label=False")
