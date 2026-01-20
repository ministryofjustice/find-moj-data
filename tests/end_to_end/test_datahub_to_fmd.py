from urllib.parse import urlparse

import pytest
from selenium.webdriver.common.by import By


@pytest.mark.slow
@pytest.mark.datahub
class TestDatahubToFindMoJdata:
    """
    Test that Find MOJ data works with a real Datahub backend.
    The datahub mark is used to bypass the `mock_catalogue` fixture.
    """

    @pytest.fixture(autouse=True)
    def setup(self, live_server, selenium):
        self.selenium = selenium
        self.live_server_url = live_server.url

    def test_table_links_to_database(self):
        """
        Browse to the first table in a subject area, and check
        we can navigate to the parent database via the breadcrumb
        """
        self.navigate_to_table()

        breadcrumbs = self.selenium.find_elements(By.CLASS_NAME, "govuk-breadcrumbs__link")
        assert len(breadcrumbs) == 3

        search_breadcrumb, database_breadcrumb, current_breadcrumb = breadcrumbs

        assert search_breadcrumb.text == "Search"
        assert urlparse(search_breadcrumb.get_attribute("href")).path.startswith("/search")

        assert urlparse(database_breadcrumb.get_attribute("href")).path.startswith("/details/database/")
        assert current_breadcrumb.get_attribute("href") == self.selenium.current_url

        database_breadcrumb.click()

        assert urlparse(self.selenium.current_url).path.startswith("/details/database/")

    def navigate_to_table(self):
        self.selenium.get(f"{self.live_server_url}")

        subject_area_list = self.selenium.find_element(By.ID, "subject-area-list")
        subject_area_list.find_element(By.PARTIAL_LINK_TEXT, "Bold").click()
        self.selenium.find_element(By.CSS_SELECTOR, "input[value='TABLE']").click()

        search_results = self.selenium.find_element(By.ID, "search-results")
        search_results.find_element(By.TAG_NAME, "a").click()
