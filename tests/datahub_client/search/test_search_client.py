from unittest.mock import MagicMock

import pytest

from datahub_client.entities import (
    AccessInformation,
    ChartEntityMapping,
    DatabaseEntityMapping,
    DataSummary,
    EntityRef,
    FurtherInformation,
    GlossaryTermEntityMapping,
    SecurityClassification,
    SubjectAreaTaxonomy,
    TableEntityMapping,
    TagRef,
    UsageRestrictions,
)
from datahub_client.search.search_client import SearchClient
from datahub_client.search.search_types import (
    FacetOption,
    MultiSelectFilter,
    SearchFacets,
    SearchResponse,
    SearchResult,
    SortOption,
    TagItem,
)


@pytest.fixture
def mock_graph():
    return MagicMock()


@pytest.fixture
def searcher(mock_graph):
    return SearchClient(mock_graph)


def test_empty_search_results(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 0,
            "total": 0,
            "searchResults": [],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    assert response == SearchResponse(total_results=0, page_results=[])


def test_no_search_results(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 0,
            "total": 0,
            "searchResults": [],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=0,
        page_results=[],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


@pytest.mark.django_db
def test_one_search_result(mock_graph, searcher):
    subject_area = SubjectAreaTaxonomy.get_by_name("Prisons and probation")
    assert subject_area

    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "container": {
                            "urn": "urn:li:container:abc",
                            "properties": {
                                "name": "abc",
                                "qualifiedName": None,
                            },
                        },
                        "ownership": None,
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                        "properties": {
                            "name": "customers",
                            "qualifiedName": "jaffle_shop.customers",
                            "customProperties": [
                                {"key": "dataSensitivity", "value": "OFFICIAL"},
                            ],
                        },
                        "tags": {
                            "tags": [
                                {
                                    "tag": {
                                        "name": subject_area.display_name,
                                        "urn": subject_area.urn,
                                    }
                                }
                            ]
                        },
                    },
                }
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                display_name="customers",
                fully_qualified_name="jaffle_shop.customers",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                subject_areas=[
                    TagRef(
                        urn="urn:li:tag:Prisons and probation",
                        display_name="Prisons and probation",
                    )
                ],
                last_modified=None,
                created=None,
                parent_entity=EntityRef(urn="urn:li:container:abc", display_name="abc"),
            )
        ],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


@pytest.mark.django_db
def test_dataset_result(mock_graph, searcher):
    subject_area = SubjectAreaTaxonomy.get_by_name("Prisons and probation")
    assert subject_area

    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "container": None,
                        "ownership": None,
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                        "properties": {
                            "name": "customers",
                            "qualifiedName": "jaffle_shop.customers",
                            "customProperties": [
                                {"key": "StoredAsSubDirectories", "value": "False"},
                                {
                                    "key": "CreatedByJob",
                                    "value": "moj-reg-prod-hmpps-assess-risks-and-needs-prod-glue-job",
                                },
                            ],
                        },
                        "tags": {
                            "tags": [
                                {
                                    "tag": {
                                        "name": subject_area.display_name,
                                        "urn": subject_area.urn,
                                    }
                                }
                            ]
                        },
                    },
                }
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                display_name="customers",
                fully_qualified_name="jaffle_shop.customers",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                subject_areas=[
                    TagRef(
                        urn="urn:li:tag:Prisons and probation",
                        display_name="Prisons and probation",
                    )
                ],
                last_modified=None,
                created=None,
            )
        ],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


def test_bad_entity_type(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "UNKNOWN",
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "container": None,
                        "ownership": None,
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                    },
                }
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = expected = SearchResponse(
        total_results=1,
        page_results=[],
        malformed_result_urns=[
            "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)"
        ],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


@pytest.mark.django_db
def test_2_dataset_results_with_one_malformed_result(mock_graph, searcher):
    subject_area = SubjectAreaTaxonomy.get_by_name("Prisons and probation")
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "container": None,
                        "ownership": None,
                        "name": "pagoda",
                        "properties": {
                            "name": "customers",
                            "qualifiedName": "jaffle_shop.customers",
                            "customProperties": [
                                {"key": "StoredAsSubDirectories", "value": "False"},
                                {
                                    "key": "CreatedByJob",
                                    "value": "moj-reg-prod-hmpps-assess-risks-and-needs-prod-glue-job",
                                },
                            ],
                        },
                        "tags": {
                            "tags": [
                                {
                                    "tag": {
                                        "name": subject_area.display_name,
                                        "urn": subject_area.urn,
                                    }
                                }
                            ]
                        },
                    },
                },
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "malformed",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "container": None,
                        "ownership": 12345,
                        "name": "john",
                        "properties": {
                            "name": "customers",
                            "qualifiedName": "jaffle_shop.customers",
                            "customProperties": [
                                {"key": "StoredAsSubDirectories", "value": "False"},
                                {
                                    "key": "CreatedByJob",
                                    "value": "moj-reg-prod-hmpps-assess-risks-and-needs-prod-glue-job",
                                },
                            ],
                        },
                    },
                },
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                display_name="customers",
                fully_qualified_name="jaffle_shop.customers",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                subject_areas=[subject_area],
                last_modified=None,
                created=None,
            )
        ],
        malformed_result_urns=["malformed"],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


def test_full_page(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 3,
            "total": 5,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "platform": {"name": "bigquery"},
                        "ownership": None,
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                        "properties": {
                            "name": "customers",
                            "qualifiedName": "jaffle_shop.customers",
                        },
                        "editableProperties": None,
                        "tags": None,
                        "lastIngested": 1705990502353,
                    },
                },
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers2,PROD)",  # noqa E501
                        "name": "calm-pagoda-323403.jaffle_shop.customers2",
                        "properties": {"name": "customers2", "qualifiedName": None},
                    },
                },
                {
                    "insights": [],
                    "matchedFields": [],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers3,PROD)",  # noqa E501
                        "name": "calm-pagoda-323403.jaffle_shop.customers3",
                        "properties": {
                            "name": "customers3",
                        },
                    },
                },
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=5,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                fully_qualified_name="jaffle_shop.customers",
                display_name="customers",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            ),
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers2,PROD)",
                result_type=TableEntityMapping,
                name="customers2",
                fully_qualified_name="calm-pagoda-323403.jaffle_shop.customers2",
                display_name="customers2",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            ),
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers3,PROD)",
                result_type=TableEntityMapping,
                name="customers3",
                fully_qualified_name="calm-pagoda-323403.jaffle_shop.customers3",
                display_name="customers3",
                description="",
                matches={},
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            ),
        ],
        facets=SearchFacets(facets={}),
    )

    assert response == expected


def test_query_match(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [
                        {
                            "name": "urn",
                            "value": "urn:li:dataset:(urn:li:dataPlatform:looker,long_tail_companions.view.customer_focused,PROD)",  # noqa E501
                        },
                        {"name": "name", "value": "customer_focused"},
                        {
                            "name": "customProperties",
                            "value": "sensitivityLevel=OFFICIAL",
                        },
                    ],
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                        "properties": {
                            "name": "customers",
                        },
                    },
                }
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                display_name="customers",
                fully_qualified_name="calm-pagoda-323403.jaffle_shop.customers",
                description="",
                matches={
                    "urn": "urn:li:dataset:(urn:li:dataPlatform:looker,long_tail_companions.view.customer_focused,PROD)",  # noqa E501
                    "name": "customer_focused",
                    "sensitivityLevel": "OFFICIAL",
                },
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            )
        ],
        facets=SearchFacets(facets={}),
    )
    assert expected == response


def test_result_with_owner(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "entity": {
                        "type": "DATASET",
                        "subTypes": {"typeNames": ["Table"]},
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",  # noqa E501
                        "name": "calm-pagoda-323403.jaffle_shop.customers",
                        "ownership": {
                            "owners": [
                                {
                                    "owner": {
                                        "urn": "urn:li:corpuser:shannon@longtail.com",
                                        "properties": {
                                            "fullName": "Shannon Lovett",
                                            "email": "shannon@longtail.com",
                                        },
                                    },
                                    "ownershipType": {
                                        "urn": "urn:li:ownershipType:__system__dataowner"
                                    },
                                }
                            ]
                        },
                        "properties": {
                            "name": "customers",
                        },
                    },
                }
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,calm-pagoda-323403.jaffle_shop.customers,PROD)",
                result_type=TableEntityMapping,
                name="customers",
                display_name="customers",
                fully_qualified_name="calm-pagoda-323403.jaffle_shop.customers",
                description="",
                matches={},
                metadata={
                    "owner": "Shannon Lovett",
                    "owner_email": "shannon@longtail.com",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            )
        ],
        facets=SearchFacets(facets={}),
    )

    assert response == expected


def test_filter(searcher, mock_graph):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 0,
            "total": 0,
            "searchResults": [],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search(filters=[MultiSelectFilter("tags", ["Abc", "Def"])])

    assert response == SearchResponse(
        total_results=0,
        page_results=[],
    )


def test_sort(searcher, mock_graph):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 0,
            "total": 0,
            "searchResults": [],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search(sort=SortOption(field="name", ascending=False))

    assert response == SearchResponse(
        total_results=0,
        page_results=[],
    )


def test_search_results_with_facets(searcher, mock_graph):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 10,
            "total": 10,
            "searchResults": [],
            "facets": [
                {
                    "field": "_entityType",
                    "displayName": "Type",
                    "aggregations": [
                        {"value": "DATASET", "count": 1505, "entity": None}
                    ],
                },
                {
                    "field": "glossaryTerms",
                    "displayName": "Glossary Term",
                    "aggregations": [
                        {
                            "value": "urn:li:glossaryTerm:SecurityClassification.Sensitive",
                            "count": 1,
                            "entity": {"properties": {"name": "Sensitive"}},
                        },
                        {
                            "value": "urn:li:glossaryTerm:Silver",
                            "count": 1,
                            "entity": {"properties": None},
                        },
                    ],
                },
                {
                    "field": "domains",
                    "displayName": "Domain",
                    "aggregations": [
                        {
                            "value": "urn:li:domain:094dc54b-0ebc-40a6-a4cf-e1b75e8b8089",
                            "count": 7,
                            "entity": {"properties": {"name": "Pet Adoptions"}},
                        },
                        {
                            "value": "urn:li:domain:7186eeff-a860-4b0a-989f-69473a0c9c67",
                            "count": 4,
                            "entity": {"properties": {"name": "E-Commerce"}},
                        },
                    ],
                },
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()

    assert response == SearchResponse(
        total_results=10,
        page_results=[],
        facets=SearchFacets(
            {
                "glossaryTerms": [
                    FacetOption(
                        value="urn:li:glossaryTerm:SecurityClassification.Sensitive",
                        label="Sensitive",
                        count=1,
                    ),
                    FacetOption(
                        value="urn:li:glossaryTerm:Silver",
                        label="urn:li:glossaryTerm:Silver",
                        count=1,
                    ),
                ],
                "domains": [
                    FacetOption(
                        value="urn:li:domain:094dc54b-0ebc-40a6-a4cf-e1b75e8b8089",
                        label="Pet Adoptions",
                        count=7,
                    ),
                    FacetOption(
                        value="urn:li:domain:7186eeff-a860-4b0a-989f-69473a0c9c67",
                        label="E-Commerce",
                        count=4,
                    ),
                ],
            }
        ),
    )


def test_get_glossary_terms(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 2,
            "total": 2,
            "searchResults": [
                {
                    "entity": {
                        "urn": "urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                        "subTypes": {"typeNames": ["Publication dataset"]},
                        "properties": {
                            "name": "IAO",
                            "description": "Information asset owner.\n",
                        },
                        "parentNodes": {
                            "nodes": [
                                {
                                    "properties": {
                                        "name": "Data protection terms",
                                        "description": "Data protection terms",
                                    }
                                }
                            ]
                        },
                    }
                },
                {
                    "entity": {
                        "urn": "urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                        "subTypes": {"typeNames": ["Publication dataset"]},
                        "properties": {
                            "name": "Security classification",
                            "description": "Only data that is 'official'",
                        },
                        "parentNodes": {"nodes": []},
                    }
                },
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.get_glossary_terms(count=2)

    assert response == SearchResponse(
        total_results=2,
        page_results=[
            SearchResult(
                urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                name="IAO",
                display_name="IAO",
                fully_qualified_name="IAO",
                description="Information asset owner.\n",
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
                result_type=GlossaryTermEntityMapping,
            ),
            SearchResult(
                urn="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                name="Security classification",
                display_name="Security classification",
                fully_qualified_name="Security classification",
                description="Only data that is 'official'",
                metadata={"parentNodes": []},
                result_type=GlossaryTermEntityMapping,
            ),
        ],
    )


def test_search_for_charts(mock_graph, searcher):
    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [
                        {
                            "name": "urn",
                            "value": "urn:li:chart:(justice-data,absconds)",
                        },
                        {
                            "name": "description",
                            "value": "test",
                        },
                        {"name": "title", "value": "absconds"},
                        {"name": "title", "value": "Absconds"},
                    ],
                    "entity": {
                        "type": "CHART",
                        "subTypes": None,
                        "urn": "urn:li:chart:(justice-data,absconds)",
                        "platform": {"name": "justice-data"},
                        "ownership": None,
                        "properties": {
                            "name": "Absconds",
                            "description": "test",
                            "externalUrl": "https://data.justice.gov.uk/prisons/public-protection/absconds",
                            "customProperties": [],
                        },
                    },
                }
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:chart:(justice-data,absconds)",
                result_type=ChartEntityMapping,
                name="Absconds",
                display_name="Absconds",
                fully_qualified_name="Absconds",
                description="test",
                matches={
                    "urn": "urn:li:chart:(justice-data,absconds)",
                    "description": "test",
                    "title": "Absconds",
                },
                metadata={
                    "owner": "",
                    "owner_email": "",
                    "total_parents": 0,
                    "dpia_required": None,
                    "dpia_location": "",
                    "dc_where_to_access_dataset": "",
                    "source_dataset_name": "",
                    "s3_location": "",
                    "dc_access_requirements": "",
                    "refresh_period": "",
                    "row_count": "",
                },
                tags=[],
                last_modified=None,
                created=None,
            )
        ],
        facets=SearchFacets(facets={}),
    )

    assert expected == response


@pytest.mark.django_db
def test_search_for_container(mock_graph, searcher):
    subject_area = SubjectAreaTaxonomy.get_by_name("Prisons and probation")
    assert subject_area

    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 1,
            "total": 1,
            "searchResults": [
                {
                    "insights": [],
                    "matchedFields": [
                        {
                            "name": "urn",
                            "value": "urn:li:container:test_db",
                        },
                        {
                            "name": "description",
                            "value": "test",
                        },
                        {"name": "name", "value": "test_db"},
                    ],
                    "entity": {
                        "type": "CONTAINER",
                        "urn": "urn:li:container:test_db",
                        "platform": {"name": "athena"},
                        "subTypes": {"typeNames": ["Database"]},
                        "ownership": {
                            "owners": [
                                {
                                    "owner": {
                                        "urn": "urn:li:corpuser:shannon@longtail.com",
                                        "properties": {
                                            "fullName": "Shannon Lovett",
                                            "email": "shannon@longtail.com",
                                        },
                                    },
                                    "ownershipType": {
                                        "urn": "urn:li:ownershipType:__system__dataowner"
                                    },
                                }
                            ]
                        },
                        "properties": {
                            "name": "test_db",
                            "description": "test",
                            "customProperties": [
                                {"key": "dpia_required", "value": "False"},
                            ],
                        },
                        "tags": {
                            "tags": [
                                {
                                    "tag": {
                                        "urn": "urn:li:tag:test",
                                        "properties": {
                                            "name": "test",
                                            "description": "test tag",
                                        },
                                    }
                                },
                                {
                                    "tag": {
                                        "name": subject_area.display_name,
                                        "urn": subject_area.urn,
                                    }
                                },
                            ]
                        },
                    },
                }
            ],
        }
    }

    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.search()
    expected = SearchResponse(
        total_results=1,
        page_results=[
            SearchResult(
                urn="urn:li:container:test_db",
                result_type=DatabaseEntityMapping,
                name="test_db",
                display_name="test_db",
                fully_qualified_name="test_db",
                description="test",
                matches={
                    "urn": "urn:li:container:test_db",
                    "description": "test",
                    "name": "test_db",
                },
                metadata={
                    "security_classification": SecurityClassification.OFFICIAL_SENSITIVE.value,  # noqa E501
                    "owner": "Shannon Lovett",
                    "owner_email": "shannon@longtail.com",
                    "readable_name": "",
                    "usage_restrictions": UsageRestrictions(
                        dpia_required=False,
                        dpia_location="",
                    ),
                    "access_information": AccessInformation(
                        dc_where_to_access_dataset="",
                        source_dataset_name="",
                        s3_location="",
                    ),
                    "data_summary": DataSummary(),
                    "further_information": FurtherInformation(),
                },
                tags=[
                    TagRef(display_name="test", urn="urn:li:tag:test"),
                ],
                subject_areas=[subject_area],
                last_modified=None,
                created=None,
            )
        ],
        facets=SearchFacets(facets={}),
    )
    assert response == expected


@pytest.mark.parametrize(
    "tags, result",
    [
        (["Electronic monitoring"], ["Electronic monitoring"]),
        (["Invalid Tag", "Prison", "Probation"], ["Prison", "Probation"]),
        (["Risk", "Reoffending"], ["Risk", "Reoffending"]),
    ],
)
def test_tag_to_display(tags, result):
    test_search_result = SearchResult(
        urn="urn:li:dataset:(urn:li:dataPlatform:athena,test_db.test_table,PROD)",
        result_type=TableEntityMapping,
        name="test_table",
        display_name="test_table",
        fully_qualified_name="test_db.test_table",
        description="just for test",
        matches={},
        metadata={
            "owner": "",
            "owner_email": "",
            "total_parents": 0,
            "parents": [],
            "dpia_required": None,
            "dpia_location": "",
            "dc_where_to_access_dataset": "",
            "source_dataset_name": "",
            "s3_location": "",
            "row_count": "",
        },
        tags=[TagRef(display_name=t, urn=f"urn:li:tag:{t}") for t in tags],
        last_modified=None,
        created=None,
    )

    assert test_search_result.tags_to_display == result


def test_get_tags(mock_graph, searcher):

    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
            "count": 200,
            "total": 3,
            "searchResults": [
                {"entity": {"urn": "urn:li:tag:tag1"}},
                {"entity": {"urn": "urn:li:tag:tag2"}},
                {"entity": {"urn": "urn:li:tag:tag3"}},
            ],
        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)

    response = searcher.get_tags()

    assert response == [
        ("tag1", "urn:li:tag:tag1"),
        ("tag2", "urn:li:tag:tag2"),
        ("tag3", "urn:li:tag:tag3"),
    ]


def test_dynamic_tags(mock_graph, searcher):
    subject_area = SubjectAreaTaxonomy.get_by_name("Prisons and probation")
    assert subject_area

    datahub_response = {
        "searchAcrossEntities": {
            "start": 0,
                "count": 4,
            "total": 4,
            "searchResults": [],
            "facets":[
                {'field': 'tags', 'displayName': 'Tag', 'aggregations': [{'value': 'urn:li:tag:Prisons and probation', 'count': 4, 'entity': {'properties': {'name': 'Prisons and probation'}}}                                                                         ]
                 }],
            "tags": ['"afasdfsad'],


        }
    }
    mock_graph.execute_graphql = MagicMock(return_value=datahub_response)
    response = searcher.search()
    tag = TagItem()
    tag.name = "Prisons and probation"
    tag.slug = "Prisons+and+probation"
    tag.count = 4

    expected = SearchResponse(
        total_results=4,
        page_results=[],
        tags=[tag],
    )
    print("expected")
    print(expected)
    print("response")
    print(response)

    assert response == expected
