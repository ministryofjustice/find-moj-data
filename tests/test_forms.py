from home.forms.search import SearchForm


class TestSearchForm:

    def test_domain_is_from_domain_list_false(self):
        assert not SearchForm(data={"domain": ["fake"]}).is_valid()

    def test_sort_is_from_sort_list_false(self):
        assert not SearchForm(data={"sort": ["fake"]}).is_valid()

    def test_all_fields_nullable(self):
        assert SearchForm(data={}).is_valid()

    def test_form_encode_without_filter_for_one_filter(self, valid_form, valid_domain):
        assert valid_form.encode_without_filter(
            filter_name="domain", filter_value=valid_domain.urn
        ) == (
            "?query=test&"
            "where_to_access=analytical_platform&"
            "entity_types=TABLE&"
            "sort=ascending&"
            "clear_filter=False&"
            "clear_label=False&"
            "tags=tag-1"
        )

    def test_form_encode_without_filter_for_two_filters(self):
        two_filter_form = SearchForm(
            data={
                "query": "test",
                "domain": "urn:li:domain:prisons",
                "entity_types": ["TABLE"],
            }
        )
        two_filter_form.is_valid()

        assert two_filter_form.encode_without_filter(
            filter_name="domain", filter_value="urn:li:domain:prisons"
        ) == (
            "?query=test&"
            "entity_types=TABLE&"
            "sort=&"
            "clear_filter=False&"
            "clear_label=False"
        )
