import logging
from typing import NamedTuple

from data_platform_catalogue.search_types import SearchFacets

logger = logging.getLogger(__name__)


class Domain(NamedTuple):
    urn: str
    label: str
    assets: int


class DomainModel:
    """
    Store information about domains and subdomains
    """

    def __init__(self, search_facets: SearchFacets):
        self.labels = {}

        self.top_level_domains = [
            Domain(option.value, option.label, option.count)
            for option in search_facets.options("domains")
        ]
        self.top_level_domains.sort(key=lambda d: d.label)

        logger.info(f"{self.top_level_domains=}")

        self.subdomains = {}

        for urn, label, assets in self.top_level_domains:
            self.labels[urn] = label

    def all_subdomains(self) -> list[Domain]:  # -> list[Any]
        """
        A flat list of all subdomains
        """
        subdomains = []
        for domain_choices in self.subdomains.values():
            subdomains.extend(domain_choices)
        return subdomains

    def get_parent_urn(self, child_subdomain_urn) -> str | None:
        for domain, subdomains in self.subdomains.items():
            for subdomain in subdomains:
                if child_subdomain_urn == subdomain.urn:
                    return domain

    def get_label(self, urn):
        return self.labels.get(urn, urn)
