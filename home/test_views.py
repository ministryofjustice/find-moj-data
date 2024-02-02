from unittest import skip

from django.test import SimpleTestCase
from django.urls import reverse


class SearchViewTests(SimpleTestCase):
    """
    Test the view renders the correct context depending on query parameters and session

    TODO: this should stub out the search client and use dummy results
    """

    def test_renders_200(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)

    def test_exposes_results(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 20)

    @skip("possibly broken")
    def test_exposes_domains(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_domain"], {})
        self.assertGreater(len(response.context["domains"]), 0)

    def test_exposes_empty_query(self):
        response = self.client.get(reverse("home:search"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "")

    def test_exposes_query(self):
        response = self.client.get(
            reverse("home:search"), data={"query": "foo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["query"], "foo")

    @skip("possibly broken")
    def test_exposes_filter(self):
        response = self.client.get(
            reverse("home:search"), data={"domain": ["urn:li:domain:HMCTS"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_domain"], {
                "urn:li:domain:HMCTS": "HMCTS"}
        )
        self.assertEqual(len(response.context["domains"]), 0)

    @skip("possibly broken")
    def test_exposes_filter_and_query(self):
        response = self.client.get(
            reverse("home:search"),
            data={"domain": ["urn:li:domain:HMCTS"], "query": "courts"},
        )
        self.assertEqual(
            response.context["selected_domain"], {
                "urn:li:domain:HMCTS": "HMCTS"}
        )
        self.assertEqual(response.context["query"], "courts")
