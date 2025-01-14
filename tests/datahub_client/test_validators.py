import pytest
from data_platform_catalogue.entities import Entity


def test_entity_timestamps_in_future_validation(entity_data_with_timestamps_in_future):
    with pytest.raises(ValueError) as exc:
        Entity(**entity_data_with_timestamps_in_future)

    assert "timestamp must be in the past" in str(exc.value)
