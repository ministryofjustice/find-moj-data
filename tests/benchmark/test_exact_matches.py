import pytest

from home.forms.search import SearchForm
from home.service.search import SearchService


@pytest.mark.slow
@pytest.mark.datahub
@pytest.mark.parametrize(
    "query,expected_urn",
    [
        (
            "prison_population_history.chunk_assignment",
            "urn:li:dataset:(urn:li:dataPlatform:dbt,awsdatacatalog.prison_population_history.chunk_assignment,PROD)",
        ),
        (
            "Accommodation on the first night following release",
            "urn:li:chart:(justice-data,accommodation-on-release)",
        ),
        (
            "vcms_activations",
            "urn:li:dataset:(urn:li:dataPlatform:dbt,awsdatacatalog.alpha_vcms_data.vcms_activations,PROD)",
        ),
        (
            "ns_postcode_lookup_latest_2011census",
            "urn:li:dataset:(urn:li:dataPlatform:dbt,awsdatacatalog.common_lookup.ns_postcode_lookup_latest_2011census,PROD)",
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
