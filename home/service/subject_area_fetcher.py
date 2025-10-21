from django.core.cache import cache

from datahub_client.search.search_types import SubjectAreaOption

from .base import GenericService


class SubjectAreaFetcher(GenericService):
    """
    Fetches subject areas with the total number of associated entities from the backend.
    """

    def __init__(
        self, filter_zero_entities: bool = True, sort_total_descending: bool = False
    ):
        self.client = self._get_catalogue_client()
        self.cache_key = "list_subject_areas"
        self.cache_timeout_seconds = 300
        self.filter_zero_entities = filter_zero_entities
        self.sort_total_descending = sort_total_descending

    def filter_and_sort(
        self, subject_areas: list[SubjectAreaOption]
    ) -> list[SubjectAreaOption]:
        result = subject_areas
        if self.filter_zero_entities:
            result = [subject_area for subject_area in result if subject_area.total > 0]

        # We want 'Miscellaneous' to always be last, so we obtain the index and pop it out.
        miscellanoeus_sa_index = next(
            (i for i, d in enumerate(result) if d.urn == "urn:li:tag:Miscellaneous"),
            None,
        )
        miscellanouse_sa = None
        if miscellanoeus_sa_index is not None:
            miscellanouse_sa = result.pop(miscellanoeus_sa_index)

        if self.sort_total_descending:
            # Sort by total descending
            result = sorted(result, key=lambda d: d.total, reverse=True)
        else:
            # Sort by name ascending
            result = sorted(result, key=lambda d: d.urn)

        # Append 'Miscellaneous' to the end of the list
        if miscellanouse_sa is not None:
            result.append(miscellanouse_sa)
        return result

    def fetch(self) -> list[SubjectAreaOption]:
        """
        Fetch a static list of options that is independent of the search query
        and any applied filters. Values are cached for 5 seconds to avoid
        unnecessary queries.
        """
        result = cache.get(self.cache_key, version=2)
        if not result:
            result = self.client.list_subject_areas()
            cache.set(self.cache_key, result, self.cache_timeout_seconds, version=2)

        result = self.filter_and_sort(result)
        return result
