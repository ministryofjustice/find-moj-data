from home.service.details import (
    DashboardDetailsService,
    DatabaseDetailsService,
    DatasetDetailsService,
)


class DatasetDetailsCsvFormatter:
    def __init__(self, details_service: DatasetDetailsService):
        self.details_service = details_service

    def data(self):
        return [
            (
                column.name,
                column.display_name,
                column.type,
                column.description,
            )
            for column in self.details_service.table_metadata.column_details
        ]

    def headers(self):
        return [
            "name",
            "display_name",
            "type",
            "description",
        ]


class DatabaseDetailsCsvFormatter:
    def __init__(self, details_service: DatabaseDetailsService):
        self.details_service = details_service

    def data(self):
        return [
            (
                table.entity_ref.urn,
                table.entity_ref.display_name,
                table.description,
            )
            for table in self.details_service.entities_in_database
        ]

    def headers(self):
        return [
            "urn",
            "display_name",
            "description",
        ]


class DashboardDetailsCsvFormatter:
    def __init__(self, details_service: DashboardDetailsService):
        self.details_service = details_service

    def data(self):
        return [
            (chart.entity_ref.urn, chart.entity_ref.display_name, chart.description)
            for chart in self.details_service.children
        ]

    def headers(self):
        return ["urn", "display_name", "description"]
