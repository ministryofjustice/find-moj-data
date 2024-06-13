import re

import pytest

from home.forms.search import SearchForm
from home.service.search import SearchService

WORD_TOKEN = re.compile(r"[^_\-\s]+")
OVERLAP_THRESHOLD = 0.75


@pytest.mark.slow
@pytest.mark.datahub
@pytest.mark.parametrize(
    "query,expected_urn",
    [
        (
            "bold_common_platform_linked_tables.all_offence",
            "urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.bold_common_platform_linked_tables.all_offence,PROD)",
        ),
        (
            "Accommodation on the first night following release",
            "urn:li:chart:(justice-data,accommodation-on-release)",
        ),
        (
            "ns_postcode_lookup_latest_2011census",
            "urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.common_lookup.ns_postcode_lookup_latest_2011census,PROD)",
        ),
    ],
)
def test_exact_title_match(query, expected_urn):
    """
    Test that tables can be retrieved by searching for their exact name
    """
    form = SearchForm({"query": query})
    assert form.is_valid()

    service = SearchService(form=form, page="1")
    results = service.results

    assert results.total_results >= 1
    assert results.page_results[0].urn == expected_urn


@pytest.mark.slow
@pytest.mark.datahub
@pytest.mark.parametrize(
    "query",
    (
        ("prison_population_history.chunk_assignment",),
        ("Accommodation on the first night following release",),
        ("vcms_activations",),
        ("ns_postcode_lookup_latest_2011census",),
    ),
)
def test_no_duplicates(query):
    """
    Test that there are no entries with similar names in the first page

    """
    form = SearchForm({"query": query})
    assert form.is_valid()

    service = SearchService(form=form, page="1")
    results = service.results

    titles = [result.fully_qualified_name for result in results.page_results]
    assert_no_fuzzy_match(titles)


def assert_no_fuzzy_match(titles):
    """
    Check for similar looking titles by tokenising and comparing the number of tokens
    common to both titles to the number of tokens that are unique to one or the other
    """
    for i, title1 in enumerate(titles, 1):
        for j, title2 in enumerate(titles, 1):
            if i == j:
                continue

            assert (
                title1 != title2
            ), f'"{title1}" @ position {i} duplicates {title2} @ position {j}"'

            tokens1 = set(WORD_TOKEN.findall(title1))
            if not tokens1:
                continue

            tokens2 = set(WORD_TOKEN.findall(title2))
            intersection = tokens1.intersection(tokens2)
            union = tokens1.union(tokens2)
            assert (
                len(intersection) / len(union) <= OVERLAP_THRESHOLD
            ), f'"{title1}" @ position {i} is similar to {title2} @ position {j}"'
