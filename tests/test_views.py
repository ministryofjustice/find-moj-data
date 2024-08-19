import pytest
from django.urls import reverse


class TestHomePage:
    def test_renders_200_with_headers(self, client):
        response = client.get(reverse("home:home"))
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"


@pytest.mark.django_db
class TestSearchView:
    """
    Test the view renders the correct context depending on query parameters and session
    """

    def test_renders_200_with_headers(self, client):
        response = client.get(reverse("home:search"), data={})
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=60, private"

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


class TestTableView:
    def test_table(self, client):
        response = client.get(
            reverse("home:details", kwargs={"urn": "fake", "result_type": "table"})
        )
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"


class TestChartView:
    def test_chart(self, client):
        response = client.get(
            reverse("home:details", kwargs={"urn": "fake", "result_type": "chart"})
        )
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"


class TestGlossaryView:
    def test_details(self, client):
        response = client.get(reverse("home:glossary"))
        assert response.status_code == 200


class TestMetadataSpecificationView:
    def test_details(self, client):
        response = client.get(reverse("home:metadata_specification"))
        assert response.status_code == 200
