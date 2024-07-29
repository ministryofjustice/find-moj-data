import logging
from typing import NamedTuple

from data_platform_catalogue.search_types import ListDomainOption

logger = logging.getLogger(__name__)


class Domain(NamedTuple):
    urn: str
    label: str


class ListDomainModel:
    def __init__(self, domains: list[ListDomainOption]):
        self.labels = {}

        self.top_level_domains = [Domain(domain.urn, domain.name) for domain in domains]
        logger.info(f"{self.top_level_domains=}")

        for urn, label in self.top_level_domains:
            self.labels[urn] = label

    def get_label(self, urn):
        return self.labels.get(urn, urn)
