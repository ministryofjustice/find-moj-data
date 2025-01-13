from typing import Sequence

from datahub_client.search_types import MultiSelectFilter


def map_filters(filters: Sequence[MultiSelectFilter] | None, entity_filters=[]):
    if filters is None:
        filters = []

    # If we have entity filters, we need the subtype filters to only apply to
    # the corresponding entity type. The resulting filter query is a union
    # of many andFilters.
    entities = [
        {
            "and": [
                {
                    "field": filter[0].filter_name,
                    "values": filter[0].included_values,
                },
                *(
                    [
                        {
                            "field": filter[1].filter_name,
                            "values": filter[1].included_values,
                        }
                    ]
                    if filter[1].included_values
                    else []
                ),
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
            ]
        }
        for filter in entity_filters
    ]

    # if there are entity filters we need to add in all other filters to each and entity block
    if entities:
        for entity in entities:
            entity["and"].extend(
                [
                    {"field": filter.filter_name, "values": filter.included_values}
                    for filter in filters
                ]
            )
            result = entities
    else:
        result = [
            {
                "and": [
                    {"field": filter.filter_name, "values": filter.included_values},
                    {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
                ]
            }
            for filter in filters
            if "urn:li:tag:dc_display_in_catalogue" not in filter.included_values
        ]

    if not result:
        result.append(
            {
                "and": [
                    {
                        "field": "tags",
                        "values": ["urn:li:tag:dc_display_in_catalogue"],
                    },
                ]
            }
        )
    return result
