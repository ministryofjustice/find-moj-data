from data_platform_catalogue.search_types import SearchFacets
from django.core.cache import cache

from .base import GenericService


class SearchFacetFetcher(GenericService):
    def __init__(self):
        self.client = self._get_catalogue_client()
        self.cache_key = "search_facets"
        self.cache_timeout_seconds = 300

    def fetch(self) -> SearchFacets:
        """
        Fetch a static list of options that is independent of the search query
        and any applied filters. Values are cached for 5 seconds to avoid
        unnecessary queries.
        """
        result = cache.get(self.cache_key)
        if not result:
            result = self.client.search_facets()
            cache.set(self.cache_key, result, timeout=self.cache_timeout_seconds)

        return result
