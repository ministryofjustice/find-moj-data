from home.service.subject_area_fetcher import SubjectAreaFetcher


class TestSubjectAreaFetcher:
    def test_list_all_subject_areas(self, mock_catalogue) -> None:
        subject_area_options = SubjectAreaFetcher(False).fetch()
        assert len(subject_area_options) == 4

    def test_list_non_empty_subject_areas(self, mock_catalogue):
        subject_area_options = SubjectAreaFetcher(True).fetch()
        assert len(subject_area_options) == 3
        assert all(
            subject_area_option.total > 0
            for subject_area_option in subject_area_options
        )
