from data_platform_catalogue.search_types import SearchResponse
from django.urls import reverse


class TestSearchView:
    """
    Test the view renders the correct context depending on query parameters and session
    """

    def test_renders_200(self, client):
        response = client.get(reverse("home:search"), data={})
        assert response.status_code == 200

    def test_exposes_results(self, client):
        response = client.get(reverse("home:search"), data={})
        assert response.status_code == 200
        assert len(response.context["results"]) == 20

    def test_exposes_empty_query(self, client):
        response = client.get(reverse("home:search"), data={})
        assert response.status_code == 200
        assert response.context["form"].cleaned_data["query"] == ""

    def test_exposes_query(self, client):
        response = client.get(reverse("home:search"), data={"query": "foo"})
        assert response.status_code == 200
        assert response.context["form"].cleaned_data["query"] == "foo"

    def test_bad_form(self, client):
        response = client.get(reverse("home:search"), data={"domain": "fake"})
        assert response.status_code == 400


class TestDetailsView:
    def test_details_data_product(self, client):
        response = client.get(
            reverse(
                "home:details",
                kwargs={
                    "id": "urn:li:dataProduct:common-platform",
                    "result_type": "data_product",
                },
            )
        )
        assert response.status_code == 200

    def test_details_data_product_not_found(self, client, mock_catalogue):
        mock_catalogue.search.return_value = SearchResponse(
            total_results=0, page_results=[]
        )
        response = client.get(
            reverse(
                "home:details", kwargs={"id": "fake", "result_type": "data_product"}
            )
        )
        assert response.status_code == 404


class TestChartView:
    def test_chart(self, client):
        response = client.get(
            reverse("home:details", kwargs={"id": "fake", "result_type": "chart"})
        )
        assert response.status_code == 200


class TestGlossaryView:
    def test_details(self, client):
        response = client.get(reverse("home:glossary"))
        assert response.status_code == 200
