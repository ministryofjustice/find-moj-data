from django.core.cache import cache

from .base import GenericService


class SearchTagFetcher(GenericService):
    def __init__(self):
        self.client = self._get_catalogue_client()
        self.cache_key = "search_tags"
        self.cache_timeout_seconds = 300

    def fetch(self) -> list:
        """
        Fetch a static list of options that is independent of the search query
        and any applied filters. Values are cached for 5 seconds to avoid
        unnecessary queries.
        """
        result = cache.get(self.cache_key, version=2)
        if not result:
            result = self.client.get_tags()

            cache.set(self.cache_key, result, timeout=self.cache_timeout_seconds, version=2)

        return result
