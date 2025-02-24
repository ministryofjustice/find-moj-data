from datahub_client.entities import GlossaryTermEntityMapping
from datahub_client.search.search_types import SearchResult
from home.service.glossary import GlossaryService


class TestGlossaryService:
    def test_get_context(self):
        glossary_context = GlossaryService()
        expected_context = {
            "h1_value": "Glossary",
            "results": [
                {
                    "name": "Data sources",
                    "members": [
                        SearchResult(
                            urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                            result_type=GlossaryTermEntityMapping,
                            name="NOMIS",
                            description="NOMIS",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data sources",
                                            "description": "Data sources",
                                        }
                                    }
                                ]
                            },
                            tags=[],
                            last_modified=None,
                        ),
                        SearchResult(
                            urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                            result_type=GlossaryTermEntityMapping,
                            name="XHIBIT",
                            description="XHIBIT",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data sources",
                                            "description": "Data sources",
                                        }
                                    }
                                ]
                            },
                            tags=[],
                            last_modified=None,
                        ),
                    ],
                    "description": "Data sources",
                    "has_entities": False,
                },
                {
                    "name": "Other technical terms",
                    "members": [
                        SearchResult(
                            urn="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                            result_type=GlossaryTermEntityMapping,
                            name="Asset",
                            description="Asset",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "description": "Other technical terms",
                                            "name": "Other technical terms",
                                        },
                                    },
                                ],
                            },
                            tags=[],
                            last_modified=None,
                        )
                    ],
                    "description": "Other technical terms",
                    "has_entities": False,
                },
            ],
        }

        assert glossary_context.context == expected_context
