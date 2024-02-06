from random import choice
from unittest import skip
from unittest.mock import MagicMock, patch

from data_platform_catalogue.client import BaseCatalogueClient
from data_platform_catalogue.search_types import (FacetOption, ResultType,
                                                  SearchFacets, SearchResponse,
                                                  SearchResult)
from django.test import SimpleTestCase
from django.urls import reverse
from faker import Faker

fake = Faker()


def generate_page(page_size=20):
    """
    Generate a fake search page
    """
    results = []
    for _ in range(page_size):
        results.append(
            SearchResult(
                id=fake.unique.name(),
                result_type=choice(
                    (ResultType.DATA_PRODUCT, ResultType.TABLE)),
                name=fake.name(),
                description=fake.paragraphs(),
            )
        )
    return results


def generate_options(num_options=5):
    """
    Generate a list of options for the search facets
    """
    results = []
    for _ in range(num_options):
        results.append(
            FacetOption(
                value=fake.name(),
                label=fake.name(),
                count=fake.random_int(min=0, max=100),
            )
        )
    return results


class SearchViewTests(SimpleTestCase):
    """
    Test the view renders the correct context depending on query parameters and session
    """

    def setUp(self):
        self.patcher = patch("home.views.get_catalogue_client")
        mock_fn = self.patcher.start()
        self.mock_client = MagicMock(spec=BaseCatalogueClient)
        mock_fn.return_value = self.mock_client
        self.mock_search_response(
            page_results=generate_page(), total_results=100)
        self.mock_search_facets_response(domains=generate_options())

    def tearDown(self):
        self.patcher.stop()

    def mock_search_response(self, total_results=0, page_results=()):
        search_response = SearchResponse(
            total_results=total_results, page_results=page_results
        )
        self.mock_client.search.return_value = search_response

    def mock_search_facets_response(self, domains):
        self.mock_client.search_facets.return_value = SearchFacets(
            {"domains": domains})

    def test_renders_200(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)

    def test_exposes_results(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 20)

    def test_exposes_empty_query(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "")

    def test_exposes_query(self):
        response = self.client.get(
            reverse("home:search"), data={"query": "foo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "foo")
