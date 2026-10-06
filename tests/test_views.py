import pytest
from django.template.loader import render_to_string
from django.urls import reverse
from waffle.testutils import override_switch

from datahub_client.entities import EntityRef, EntitySummary, RelationshipType
from tests.conftest import generate_search_result, generate_table_metadata, mock_search_response


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


@pytest.mark.django_db
class TestSearchFoundInDescription:
    """
    "Found in description" should only be shown when the search query matches the description
    """

    FOUND_IN = "Found in description"

    def search_with_description(self, client, mock_catalogue, description, query):
        result = generate_search_result()
        result.description = description
        mock_search_response(mock_catalogue, total_results=1, page_results=[result])
        response = client.get(reverse("home:search"), data={"query": query})
        assert response.status_code == 200
        return response.text

    def test_shown_when_query_matches_description(self, client, mock_catalogue):
        html = self.search_with_description(client, mock_catalogue, "Monthly prison population figures", "prison")

        assert self.FOUND_IN in html
        assert "<mark>prison</mark>" in html

    def test_shown_when_stemmed_query_matches_description(self, client, mock_catalogue):
        html = self.search_with_description(client, mock_catalogue, "Monthly prison population figures", "prisons")

        assert self.FOUND_IN in html

    def test_not_shown_when_query_does_not_match_description(self, client, mock_catalogue):
        html = self.search_with_description(client, mock_catalogue, "Monthly prison population figures", "courts")

        assert self.FOUND_IN not in html
        assert "Monthly prison population figures" not in html

    @pytest.mark.parametrize("query", ["", "*"])
    def test_not_shown_without_a_search_query(self, client, mock_catalogue, query):
        html = self.search_with_description(client, mock_catalogue, "Monthly prison population figures", query)

        assert self.FOUND_IN not in html
        assert "Monthly prison population figures" in html

    def test_not_shown_when_description_is_empty(self, client, mock_catalogue):
        html = self.search_with_description(client, mock_catalogue, "", "prison")

        assert self.FOUND_IN not in html


class TestSearchCardTemplate:
    FOUND_IN = "Found in description"

    def render_card(self, description):
        result = generate_search_result()
        result.description = description
        return render_to_string("partial/search_card.html", {"result": result})

    def test_shows_found_in_for_highlighted_description(self):
        rendered = self.render_card("Monthly <mark>prison</mark> population figures")

        assert self.FOUND_IN in rendered

    def test_hides_found_in_for_unhighlighted_description(self):
        rendered = self.render_card("Monthly prison population figures")

        assert self.FOUND_IN not in rendered
        assert "Monthly prison population figures" in rendered

    def test_hides_found_in_for_empty_description(self):
        rendered = self.render_card("")

        assert self.FOUND_IN not in rendered


class TestTableView:
    @pytest.mark.parametrize("switch_bool", [True, False])
    @pytest.mark.django_db
    def test_table(self, client, switch_bool):
        with override_switch(name="show_is_nullable_in_table_details_column", active=switch_bool):
            response = client.get(reverse("home:search"))

        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=60, private"

    @pytest.mark.django_db
    def test_csv_output(self, client):
        response = client.get(
            reverse(
                "home:details_csv",
                kwargs={"urn": "fake", "result_type": "table"},
            )
        )
        assert response.status_code == 200
        assert response.headers["Content-Disposition"] == 'attachment; filename="Foo.example_table.csv"'
        assert response.content == (
            b"name,display_name,type,description\r\n" + b"urn,urn,string,description **with markdown**\r\n"
        )

    @pytest.mark.django_db
    def test_details_metadata_partial_handles_missing_parent_urn(self):
        table_metadata = generate_table_metadata(
            relations={
                RelationshipType.PARENT: [
                    EntitySummary(
                        entity_ref=EntityRef(urn="", display_name="parent_database"),
                        description="parent description",
                        tags=[],
                        entity_type="DATABASE",
                    )
                ],
                RelationshipType.DATA_LINEAGE: [],
            }
        )

        rendered = render_to_string(
            "partial/details_metadata.html",
            {
                "entity": table_metadata,
                "entity_type": "Table",
                "parent_entity": EntityRef(urn="", display_name="parent_database"),
                "parent_type": "database",
                "is_access_requirements_a_url": False,
            },
        )

        assert "parent_database" in rendered
        assert 'href="' not in rendered


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
        assert response.headers["Content-Disposition"] == 'attachment; filename="Foo.example_database.csv"'
        assert response.content == (
            b"urn,display_name,description\r\n" + b"urn:li:dataset:fake_table,fake_table,table description\r\n"
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
        assert response.headers["Content-Disposition"] == 'attachment; filename="Foo.example_dashboard.csv"'
        assert response.content == (
            b"urn,display_name,description\r\n" + b"urn:li:chart:fake_chart,fake_chart,chart description\r\n"
        )


class TestChartView:
    @pytest.mark.django_db
    def test_chart(self, client):
        response = client.get(reverse("home:details", kwargs={"urn": "fake", "result_type": "chart"}))
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "max-age=300, private"

    @pytest.mark.django_db
    def test_details_page_renders_history_back_link_with_search_fallback(self, client):
        response = client.get(reverse("home:details", kwargs={"urn": "fake", "result_type": "chart"}))

        assert response.status_code == 200
        assert 'data-history-back-link="true"' in response.text
        assert 'href="/search?"' in response.text
        assert "Back to search results" in response.text
