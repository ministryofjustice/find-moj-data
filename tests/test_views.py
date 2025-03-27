import pytest
from django.urls import reverse
from waffle.testutils import override_switch


@pytest.mark.django_db
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
        response = client.get(reverse("home:search"), data={"subject_area": "fake"})
        assert response.status_code == 400


class TestTableView:
    @pytest.mark.parametrize("switch_bool", [True, False])
    @pytest.mark.django_db
    def test_table(self, client, switch_bool):
        with override_switch(
            name="show_is_nullable_in_table_details_column", active=switch_bool
        ):
            response = client.get(
                reverse("home:details", kwargs={"urn": "fake", "result_type": "table"})
            )

        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"

    @pytest.mark.django_db
    def test_csv_output(self, client):
        response = client.get(
            reverse(
                "home:details_csv",
                kwargs={"urn": "fake", "result_type": "table"},
            )
        )
        assert response.status_code == 200
        assert (
            response.headers["Content-Disposition"]
            == 'attachment; filename="Foo.example_table.csv"'
        )
        assert response.content == (
            b"name,display_name,type,description\r\n"
            + b"urn,urn,string,description **with markdown**\r\n"
        )


class TestDatabaseView:
    @pytest.mark.django_db
    def test_csv_output(self, client):
        response = client.get(
            reverse(
                "home:details_csv",
                kwargs={"urn": "fake", "result_type": "database"},
            )
        )
        assert response.status_code == 200
        assert (
            response.headers["Content-Disposition"]
            == 'attachment; filename="Foo.example_database.csv"'
        )
        assert response.content == (
            b"urn,display_name,description\r\n"
            + b"urn:li:dataset:fake_table,fake_table,table description\r\n"
        )


class TestDashboardView:
    @pytest.mark.django_db
    def test_csv_output(self, client):
        response = client.get(
            reverse(
                "home:details_csv",
                kwargs={"urn": "fake", "result_type": "dashboard"},
            )
        )
        assert response.status_code == 200
        assert (
            response.headers["Content-Disposition"]
            == 'attachment; filename="Foo.example_dashboard.csv"'
        )
        assert response.content == (
            b"urn,display_name,description\r\n"
            + b"urn:li:chart:fake_chart,fake_chart,chart description\r\n"
        )


class TestChartView:
    def test_chart(self, client):
        response = client.get(
            reverse("home:details", kwargs={"urn": "fake", "result_type": "chart"})
        )
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"


class TestGlossaryView:
    def test_list(self, client):
        response = client.get(reverse("home:glossary"))
        assert response.status_code == 200

    def test_details(self, client):
        response = client.get(reverse("home:glossary_term", kwargs={"urn": "fake"}))
        assert response.status_code == 200
