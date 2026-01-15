from datahub_client.entities import (
    FindMoJdataEntityType,
    get_entity_type_counts_from_datahub,
)


class TestGetEntityTypeCountsFromDatahub:
    """Tests for the get_entity_type_counts_from_datahub function."""

    def test_empty_counts(self):
        """When both dicts are empty, all entity types should have count 0."""
        result = get_entity_type_counts_from_datahub({}, {})

        assert result[FindMoJdataEntityType.TABLE] == 0
        assert result[FindMoJdataEntityType.CHART] == 0
        assert result[FindMoJdataEntityType.DATABASE] == 0
        assert result[FindMoJdataEntityType.DASHBOARD] == 0

    def test_entity_type_without_subtypes_uses_entity_count(self):
        """Entity types without subtypes (CHART, DASHBOARD) use entity type count."""
        entity_type_counts = {
            "CHART": 15,
            "DASHBOARD": 20,
        }
        subtype_counts = {}

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        assert result[FindMoJdataEntityType.CHART] == 15
        assert result[FindMoJdataEntityType.DASHBOARD] == 20

    def test_entity_type_with_subtypes_sums_subtype_counts(self):
        """Entity types with subtypes sum the subtype counts."""
        entity_type_counts = {
            "DATASET": 100,  # Should be ignored for TABLE
            "CONTAINER": 50,  # Should be ignored for DATABASE/SCHEMA
        }
        subtype_counts = {
            "Table": 30,
            "Model": 25,
            "Seed": 5,
            "Source": 10,
            "Database": 15,
            "Schema": 8,
        }

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        # TABLE sums Table + Model + Seed + Source
        assert result[FindMoJdataEntityType.TABLE] == 30 + 25 + 5 + 10
        # DATABASE only counts Database subtype
        assert result[FindMoJdataEntityType.DATABASE] == 15
        # SCHEMA only counts Schema subtype
        assert result[FindMoJdataEntityType.SCHEMA] == 8

    def test_publication_types_use_subtype_counts(self):
        """Publication dataset and collection use their specific subtypes."""
        entity_type_counts = {}
        subtype_counts = {
            "Publication dataset": 42,
            "Publication collection": 7,
        }

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        assert result[FindMoJdataEntityType.PUBLICATION_DATASET] == 42
        assert result[FindMoJdataEntityType.PUBLICATION_COLLECTION] == 7

    def test_glossary_term_uses_entity_type_count(self):
        """Glossary term uses entity type count (no subtypes)."""
        entity_type_counts = {
            "GLOSSARY_TERM": 100,
        }
        subtype_counts = {}

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        assert result[FindMoJdataEntityType.GLOSSARY_TERM] == 100

    def test_missing_subtypes_default_to_zero(self):
        """Missing subtypes should contribute 0 to the sum."""
        entity_type_counts = {}
        subtype_counts = {
            "Table": 50,
            # Model, Seed, Source are missing
        }

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        # Should only count Table, others default to 0
        assert result[FindMoJdataEntityType.TABLE] == 50

    def test_all_entity_types_present_in_result(self):
        """All FindMoJdataEntityType values should be present in the result."""
        result = get_entity_type_counts_from_datahub({}, {})

        for entity_type in FindMoJdataEntityType:
            assert entity_type in result

    def test_realistic_scenario(self):
        """Test with realistic data matching what DataHub might return."""
        entity_type_counts = {
            "DATASET": 500,
            "CONTAINER": 100,
            "CHART": 25,
            "DASHBOARD": 10,
            "GLOSSARY_TERM": 150,
        }
        subtype_counts = {
            "Table": 300,
            "Model": 100,
            "Seed": 20,
            "Source": 30,
            "Publication dataset": 50,
            "Database": 40,
            "Schema": 55,
            "Publication collection": 5,
        }

        result = get_entity_type_counts_from_datahub(entity_type_counts, subtype_counts)

        assert result[FindMoJdataEntityType.TABLE] == 450  # 300+100+20+30
        assert result[FindMoJdataEntityType.PUBLICATION_DATASET] == 50
        assert result[FindMoJdataEntityType.DATABASE] == 40
        assert result[FindMoJdataEntityType.SCHEMA] == 55
        assert result[FindMoJdataEntityType.PUBLICATION_COLLECTION] == 5
        assert result[FindMoJdataEntityType.CHART] == 25
        assert result[FindMoJdataEntityType.DASHBOARD] == 10
        assert result[FindMoJdataEntityType.GLOSSARY_TERM] == 150
