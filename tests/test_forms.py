from home.forms.search import SearchForm


class TestSearchForm:

    def test_rejects_unknown_subject_area(self):
        assert not SearchForm(data={"subject_area": ["fake"]}).is_valid()

    def test_rejects_unknown_sort(self):
        assert not SearchForm(data={"sort": ["fake"]}).is_valid()

    def test_all_fields_nullable(self):
        assert SearchForm(data={}).is_valid()

    def test_form_encode_without_filter_for_one_filter(
        self, valid_form, valid_subject_area_choice
    ):
        assert valid_form.encode_without_filter(
            filter_name="subject_area", filter_value=valid_subject_area_choice.urn
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
                "subject_area": "urn:li:tag:prisons",
                "entity_types": ["TABLE"],
            }
        )
        two_filter_form.is_valid()

        assert two_filter_form.encode_without_filter(
            filter_name="subject_area", filter_value="urn:li:tag:prisons"
        ) == (
            "?query=test&"
            "entity_types=TABLE&"
            "sort=&"
            "clear_filter=False&"
            "clear_label=False"
        )
