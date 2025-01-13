from datahub_client.client.search.filters import map_filters
from datahub_client.search_types import MultiSelectFilter


def test_map_filters_with_defaults():
    assert map_filters([], []) == [
        {"and": [{"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]}]}
    ]


def test_map_filters_with_entity_type():
    assert map_filters(
        [],
        [
            (
                MultiSelectFilter(
                    "_entityType",
                    ["DATASET"],
                ),
                MultiSelectFilter("typeNames", ["Model", "Seed"]),
            )
        ],
    ) == [
        {
            "and": [
                {"field": "_entityType", "values": ["DATASET"]},
                {"field": "typeNames", "values": ["Model", "Seed"]},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
            ]
        }
    ]


def test_mixing_subtypes_and_entity_type_filters():
    assert map_filters(
        [],
        [
            (
                MultiSelectFilter(
                    "_entityType",
                    ["DATASET"],
                ),
                MultiSelectFilter("typeNames", ["Model", "Seed"]),
            ),
            (
                MultiSelectFilter(
                    "_entityType",
                    ["CHART"],
                ),
                MultiSelectFilter("typeNames", []),
            ),
        ],
    ) == [
        {
            "and": [
                {"field": "_entityType", "values": ["DATASET"]},
                {"field": "typeNames", "values": ["Model", "Seed"]},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
            ]
        },
        {
            "and": [
                {"field": "_entityType", "values": ["CHART"]},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
            ]
        },
    ]


def test_multiple_entity_type_filters_plus_other_filters():
    assert map_filters(
        [
            MultiSelectFilter("someField", ["foo"]),
            MultiSelectFilter("someOtherField", ["bar", "baz"]),
        ],
        [
            (
                MultiSelectFilter(
                    "_entityType",
                    ["DATASET"],
                ),
                MultiSelectFilter("typeNames", ["Model", "Seed"]),
            ),
            (
                MultiSelectFilter(
                    "_entityType",
                    ["CHART"],
                ),
                MultiSelectFilter("typeNames", []),
            ),
        ],
    ) == [
        {
            "and": [
                {"field": "_entityType", "values": ["DATASET"]},
                {"field": "typeNames", "values": ["Model", "Seed"]},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
                {"field": "someField", "values": ["foo"]},
                {"field": "someOtherField", "values": ["bar", "baz"]},
            ]
        },
        {
            "and": [
                {"field": "_entityType", "values": ["CHART"]},
                {"field": "tags", "values": ["urn:li:tag:dc_display_in_catalogue"]},
                {"field": "someField", "values": ["foo"]},
                {"field": "someOtherField", "values": ["bar", "baz"]},
            ]
        },
    ]
