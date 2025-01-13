import logging
from typing import NamedTuple

from datahub_client.search_types import SubjectAreaOption

logger = logging.getLogger(__name__)


class SubjectArea(NamedTuple):
    urn: str
    label: str


class SubjectAreaTaxonomy:
    def __init__(self, subject_areas: list[SubjectAreaOption]):
        self.labels = {}

        self.top_level_subject_areas = [
            SubjectArea(domain.urn, domain.name) for domain in subject_areas
        ]
        logger.info(f"{self.top_level_subject_areas=}")

        for urn, label in self.top_level_subject_areas:
            self.labels[urn] = label

    def get_label(self, urn):
        return self.labels.get(urn, urn)
