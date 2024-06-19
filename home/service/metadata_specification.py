from data_platform_catalogue.entities import (
    AccessInformation,
    Chart,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Database,
    DataSummary,
    DomainRef,
    Entity,
    EntityRef,
    FurtherInformation,
    Governance,
    OwnerRef,
    Table,
    TagRef,
    UsageRestrictions,
)


class MetadataSpecificationService:
    def __init__(self):
        self.context = self._get_context()

    def _get_context(self):
        return {
            "h1_value": "Metadata specification",
            "entities": {
                "Table": Table.model_json_schema(),
                "Database": Database.model_json_schema(),
                "Chart": Chart.model_json_schema(),
                "CustomEntityProperties": CustomEntityProperties.model_json_schema(),
                "UsageRestrictions": UsageRestrictions.model_json_schema(),
                "AccessInformation": AccessInformation.model_json_schema(),
                "EntityRef": EntityRef.model_json_schema(),
                "Governance": Governance.model_json_schema(),
                "OwnerRef": OwnerRef.model_json_schema(),
                "DomainRef": DomainRef.model_json_schema(),
                "Column": Column.model_json_schema(),
                "ColumnRef": ColumnRef.model_json_schema(),
                "TagRef": TagRef.model_json_schema(),
                "DataSummary": DataSummary.model_json_schema(),
                "FurtherInformation": FurtherInformation.model_json_schema(),
                "Entity": Entity.model_json_schema(),
            },
        }
