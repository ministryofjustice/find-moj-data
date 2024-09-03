from data_platform_catalogue.search_types import DomainOption
from django.core.cache import cache

from .base import GenericService


class DomainFetcher(GenericService):
    """
    DomainFetcher implementation to fetch domains with the total number of
    associated entities from the backend.
    """

    def __init__(self, filter_zero_entities: bool = True):
        self.client = self._get_catalogue_client()
        self.cache_key = "list_domains"
        self.cache_timeout_seconds = 300
        self.filter_zero_entities = filter_zero_entities

    def fetch(self) -> list[DomainOption]:
        """
        Fetch a static list of options that is independent of the search query
        and any applied filters. Values are cached for 5 seconds to avoid
        unnecessary queries.
        """
        result = cache.get(self.cache_key)
        if not result:
            print("not found in cache")
            result = self.client.list_domains()
            result = sorted(result, key=lambda d: d.urn)
            cache.set(self.cache_key, result, timeout=self.cache_timeout_seconds)
        else:
            print("found in cache")
        if self.filter_zero_entities:
            result = [domain for domain in result if domain.total > 0]
        return result
