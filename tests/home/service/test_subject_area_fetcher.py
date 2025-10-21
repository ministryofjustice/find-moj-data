from home.service.subject_area_fetcher import SubjectAreaFetcher


class TestSubjectAreaFetcher:
    def test_remove_zero_entity_subject_areas(self, mock_catalogue) -> None:
        subject_area_options = SubjectAreaFetcher(
            filter_zero_entities=True, sort_total_descending=False
        ).fetch()
        assert len(subject_area_options) == 3

        assert all(
            subject_area_option.total > 0
            for subject_area_option in subject_area_options
        )

    def test_sort_subject_areas_by_total_descending(self, mock_catalogue) -> None:
        subject_area_options = SubjectAreaFetcher(
            filter_zero_entities=False, sort_total_descending=True
        ).fetch()
        totals = [
            subject_area_option.total for subject_area_option in subject_area_options
        ]
        assert totals == sorted(totals, reverse=True)

    def test_sort_subject_areas_by_name_ascending(self, mock_catalogue) -> None:
        subject_area_options = SubjectAreaFetcher(
            filter_zero_entities=True, sort_total_descending=False
        ).fetch()
        urns = [subject_area_option.urn for subject_area_option in subject_area_options]
        assert urns == sorted(urns)
