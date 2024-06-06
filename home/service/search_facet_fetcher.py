from data_platform_catalogue.search_types import SearchFacets

from .base import GenericService


class SearchFacetFetcher(GenericService):
    def __init__(self):
        self.client = self._get_catalogue_client()

    def fetch(self) -> SearchFacets:
        """
        Fetch a static list of options that is independent of the search query
        and any applied filters.
        TODO: this can be cached in memory to speed up future requests
        """
        return self.client.search_facets()
