"""Search types module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from datahub_client.entities import (
    ALL_FILTERABLE_TAGS,
    EntityRef,
    FindMoJdataEntityMapper,
    GlossaryTermRef,
    TagRef,
)


@dataclass
class MultiSelectFilter:
    """
    Values to filter the result set by
    """

    filter_name: str
    included_values: list[Any]


@dataclass
class SortOption:
    """Set the search result sorting."""

    field: str
    ascending: bool = True

    def format(self):
        return {
            "sortCriterion": {
                "field": self.field,
                "sortOrder": "ASCENDING" if self.ascending else "DESCENDING",
            }
        }


@dataclass
class FacetOption:
    """
    A specific value that may be used to filter the search
    """

    value: str
    label: str
    count: int


@dataclass
class SubjectAreaOption:
    """
    A representation of a subject area and the number of associated entities
    represented by total.
    """

    urn: str
    name: str
    description: str
    total: int


@dataclass
class SearchResult:
    urn: str
    result_type: FindMoJdataEntityMapper
    name: str
    display_name: str = ""
    fully_qualified_name: str = ""
    description: str = ""
    matches: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[TagRef] = field(default_factory=list)
    subject_areas: list[TagRef] = field(default_factory=list)
    glossary_terms: list[GlossaryTermRef] = field(default_factory=list)
    last_modified: datetime | None = None
    created: datetime | None = None
    parent_entity: EntityRef | None = None
    tags_to_display: list[str] = field(init=False)

    def __post_init__(self):
        self.tags_to_display = [
            tag.display_name for tag in self.tags if tag in ALL_FILTERABLE_TAGS
        ]


@dataclass
class SearchFacets:
    facets: dict[str, list[FacetOption]] = field(default_factory=dict)

    def options(self, field_name) -> list[FacetOption]:
        """
        Return a list of FacetOptions to display in a search facet.
        Each option includes label, value and count.
        Returns an empty list if there are no options to display.
        """
        return self.facets.get(field_name, [])

    def labels(self, field_name) -> list[str]:
        """
        Return a list of labels to display in a search facet.
        """
        return [f.label for f in self.options(field_name)]

    def lookup_label(self, field_name, label) -> FacetOption | None:
        """
        Return the FacetOption matching a particular label.
        """
        options = self.options(field_name)
        for option in options:
            if option.label == label:
                return option
        return None


@dataclass
class TagItem:
    name: str
    slug: str
    count: int


@dataclass
class SearchResponse:
    total_results: int
    page_results: list[SearchResult]
    malformed_result_urns: list[str] = field(default_factory=list)
    facets: SearchFacets = field(default_factory=SearchFacets)
    tags: list[TagItem | None] = field(default_factory=list)
