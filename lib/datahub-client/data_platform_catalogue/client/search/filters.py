from typing import Sequence

from data_platform_catalogue.search_types import MultiSelectFilter


def map_filters(filters: Sequence[MultiSelectFilter] | None, entity_filters=[]):
    if filters is None:
        filters = []

    other_filters = [
        {
            "and": [
                {"field": filter.filter_name, "values": filter.included_values},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
            ]
        }
        for filter in filters
        if "urn:li:tag:dc_display_in_catalogue" not in filter.included_values
    ]
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

    additional_filters = [
        condition for filter_dict in other_filters for condition in filter_dict["and"]
    ]

    # if there are entity filters we need to add in all other filters to each and entity block
    if entities:
        result = (
            [{"and": entity["and"] + additional_filters} for entity in entities]
            if additional_filters
            else entities
        )
    else:
        result = other_filters

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
