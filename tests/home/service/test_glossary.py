from data_platform_catalogue.entities import GlossaryTermEntityMapping
from data_platform_catalogue.search_types import SearchResult

from home.service.glossary import GlossaryService


class TestGlossaryService:
    def test_get_context(self):
        glossary_context = GlossaryService()
        expected_context = {
            "h1_value": "Glossary",
            "results": [
                {
                    "name": "Data protection terms",
                    "members": [
                        SearchResult(
                            urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                            result_type=GlossaryTermEntityMapping,
                            name="IAO",
                            description="Information asset owner.\n",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data protection terms",
                                            "description": "Data protection terms",
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
                            name="Other term",
                            description="Term description to test groupings work",
                            matches={},
                            metadata={
                                "parentNodes": [
                                    {
                                        "properties": {
                                            "name": "Data protection terms",
                                            "description": "Data protection terms",
                                        }
                                    }
                                ]
                            },
                            tags=[],
                            last_modified=None,
                        ),
                    ],
                    "description": "Data protection terms",
                },
                {
                    "name": "Unsorted",
                    "members": [
                        SearchResult(
                            urn="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                            result_type=GlossaryTermEntityMapping,
                            name="Security classification",
                            description="Only data that is 'official'",
                            matches={},
                            metadata={"parentNodes": []},
                            tags=[],
                            last_modified=None,
                        )
                    ],
                    "description": "",
                },
            ],
        }

        assert expected_context == glossary_context.context
