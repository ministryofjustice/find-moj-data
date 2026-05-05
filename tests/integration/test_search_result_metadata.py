import pytest

from datahub_client.entities import DatabaseEntityMapping
from datahub_client.search.search_types import SearchResult
from tests.conftest import mock_search_response


@pytest.mark.slow
class TestSearchResultMetadata:
    """
    Given I am on a search page
    When I look at the metadata underneath a search result
    Then the new metadata should be shown for results that have it
    """

    @pytest.fixture(autouse=True)
    def setup(self, live_server, selenium):
        self.selenium = selenium
        self.live_server_url = live_server.url

    def test_matched_fields_hidden(self, mock_catalogue):
        result = SearchResult(
            urn="fake-urn",
            result_type=DatabaseEntityMapping,
            name="abc",
            fully_qualified_name="abc",
            description="bla bla bla",
            matches={"tags": []},
        )
        mock_search_response(mock_catalogue, total_results=1, page_results=[result])

        self.selenium.get(f"{self.live_server_url}/search")

        assert "Matched fields" not in self.selenium.page_source

    def test_result_metadata_shown(self, mock_catalogue):
        result = SearchResult(
            urn="fake-urn",
            result_type=DatabaseEntityMapping,
            name="abc",
            fully_qualified_name="abc",
            description="bla bla bla",
            matches={"tags": []},
            tags=[],
        )
        mock_search_response(mock_catalogue, total_results=1, page_results=[result])

        self.selenium.get(f"{self.live_server_url}/search?query=bla")

        assert "Matched fields" not in self.selenium.page_source
        assert "Tags:" not in self.selenium.page_source
