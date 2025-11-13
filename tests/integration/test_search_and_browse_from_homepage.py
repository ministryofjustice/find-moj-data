import re

import pytest
from selenium.webdriver.common.keys import Keys

from .helpers import check_for_accessibility_issues


@pytest.mark.slow
class TestSearchAndBrowseFromHomepage:
    """
    Given I am on the home page
    When I search or browse
    Then I should be taken to the search page
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        home_page,
        search_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.search_page = search_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def test_search_with_query(self):
        """
        Types a search query and press enter
        """
        self.start_on_the_home_page()
        self.enter_a_query_and_submit("nomis")
        self.verify_i_am_on_the_search_page()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_i_have_results()

    def test_browse_to_subject_area(self):
        self.start_on_the_home_page()
        self.click_on_subject_area("Prisons")
        self.verify_i_am_on_the_search_page()
        self.verify_subject_area_selected("Prisons")

    def test_automated_accessibility_home(self):
        self.start_on_the_home_page()
        check_for_accessibility_issues(
            self.selenium.current_url,
            chromedriver_path=self.chromedriver_path,
            axe_version=self.axe_version,
        )

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert self.selenium.title in self.page_titles
        heading_text = self.home_page.primary_heading().text

        assert heading_text == "Ministry of Justice Find MOJ data"
        assert self.selenium.title.split("-")[0].strip() == "Home"

    def verify_i_am_on_the_search_page(self):
        assert self.selenium.title in self.page_titles
        heading_text = self.search_page.primary_heading().text

        assert heading_text == self.selenium.title.split("-")[0].strip()

    def verify_i_have_results(self):
        result_count = self.search_page.result_count().text
        assert re.match(r"[1-9]\d* results", result_count)

    def enter_a_query_and_submit(self, query):
        search_bar = self.home_page.search_bar()
        search_bar.send_keys(query)
        search_bar.send_keys(Keys.ENTER)

    def verify_the_search_bar_has_value(self, query):
        search_bar = self.search_page.search_bar()

        assert search_bar.get_attribute("value") == query

    def click_on_subject_area(self, subject_area):
        self.home_page.subject_area_link(subject_area).click()

    def verify_subject_area_selected(self, subject_area):
        selected_subject_area = self.search_page.get_selected_subject_area().text
        assert selected_subject_area == subject_area
