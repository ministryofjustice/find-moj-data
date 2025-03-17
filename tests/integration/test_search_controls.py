import re

import pytest
from selenium.webdriver.common.by import By

from .helpers import check_for_accessibility_issues


@pytest.mark.slow
class TestSearchInteractions:
    """
    Given I am on the search page
    When I interact with the search bar, filters, or pagination options
    Then the form is resubmitted and my choices should persist
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        search_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.search_page = search_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def test_search_with_query(self):
        """
        Types a search query and press enter
        """
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("nomis")
        self.verify_i_am_on_the_search_page()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_i_have_results()

    def test_apply_subject_area_filters(self):
        """
        Interacts with the filters on the left hand side
        """
        subject_area = "Prisons"
        self.start_on_the_search_page()
        self.select_subject_area(subject_area)
        self.verify_i_am_on_the_search_page()
        self.verify_i_have_results()
        self.verify_subject_area_selected(subject_area)

    def test_pagination(self):
        """
        Interact with the pagination component
        """
        self.start_on_the_search_page()
        self.verify_page("1")
        self.click_next_page()
        self.verify_page("2")
        self.click_previous_page()
        self.verify_page("1")

    @pytest.mark.skip(reason="search sort is currently switched off")
    def test_sorting(self):
        """
        Interact with the sort control. Note: without javascript, this requires
        the form to be submitted by pressing a button.
        """
        self.start_on_the_search_page()

        # FIXME: this isn't preselected if the `new` query param is missing
        self.verify_sort_selected("Relevance")

        self.click_option("Ascending")
        self.click_on_the_search_button()
        self.verify_i_have_results()
        self.verify_sort_selected("Ascending")

    @pytest.mark.skip(reason="search sort is currently switched off")
    def test_filters_query_and_sort_persist(self):
        """
        Search settings persist as the user continues to
        interact with the search page.
        """
        subject_area = "Prisons"
        self.start_on_the_search_page()
        self.select_subject_area(subject_area)
        self.enter_a_query_and_submit("nomis")
        self.click_option("Ascending")
        self.click_on_the_search_button()

        self.verify_i_have_results()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_subject_area_selected(subject_area)
        self.verify_sort_selected("Ascending")

    def test_adding_a_query_resets_pagination(self):
        """
        Entering a new search query changes the result set,
        so it should reset the page number.
        """
        self.start_on_the_search_page()
        self.click_next_page()
        self.verify_page("2")
        self.enter_a_query_and_submit("nomis")
        self.verify_page("1")

    def test_adding_a_filter_resets_pagination(self):
        """
        Adding a filter changes the result set,
        so it should reset the page number.
        """
        self.start_on_the_search_page()
        self.click_next_page()
        self.verify_page("2")
        self.select_subject_area("Prisons")
        self.verify_page("1")

    def test_clear_single_filter(self):
        """
        Users can clear a filter by clicking on it within the "selected filters"
        panel.
        """
        subject_area = "Prisons"
        self.start_on_the_search_page()
        self.select_subject_area(subject_area)
        self.verify_subject_area_selected(subject_area)
        self.click_clear_selected_filter(subject_area)
        self.verify_unselected_subject_area()

    def test_clear_all_filters(self):
        """
        Users can click a button to clear all filters.
        """
        subject_area = "Prisons"

        self.start_on_the_search_page()

        filters = self.search_page.get_all_filter_names()
        self.select_subject_area(subject_area)
        for filter in filters:
            self.click_option(filter)
            self.search_page.sleep(0.01)
        self.verify_subject_area_selected(subject_area)
        self.verify_checkbox_filters_selected(filters)
        self.click_clear_filters()
        self.verify_unselected_subject_area()
        self.verfiy_unselected_checkbox_filters()

    def test_automated_accessibility_search(self):
        self.start_on_the_search_page()
        check_for_accessibility_issues(
            self.selenium.current_url,
            chromedriver_path=self.chromedriver_path,
            axe_version=self.axe_version,
        )

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search?new=True")
        assert self.selenium.title in self.page_titles

    def click_on_the_search_button(self):
        self.search_page.search_button().click()

    def verify_checkbox_filters_selected(self, filters):
        selected_filters = self.search_page.get_selected_checkbox_filter_names()
        assert selected_filters == filters

    def verfiy_unselected_checkbox_filters(self):
        selected_filters = self.search_page.get_selected_checkbox_filter_names()
        assert selected_filters == []

    def verify_i_am_on_the_search_page(self):
        assert self.selenium.title in self.page_titles
        heading_text = self.search_page.primary_heading().text

        assert heading_text == self.selenium.title.split("-")[0].strip()

    def verify_i_have_results(self):
        result_count = self.search_page.result_count().text
        assert re.match(r"[1-9]\d* results", result_count)

    def click_on_the_first_result(self):
        first_result = self.search_page.first_search_result()
        assert first_result.text

        first_link = first_result.link()
        item_name = first_link.text
        first_link.click()
        return item_name

    def enter_a_query_and_submit(self, query):
        search_bar = self.search_page.search_bar()
        search_bar.send_keys(query)
        self.click_on_the_search_button()
        self.search_page.wait_for_element_to_be_visible(By.ID, "result-count")

    def select_subject_area(self, subject_area):
        self.search_page.select_subject_area(subject_area)

    def click_option(self, sortby):
        self.search_page.sort_label(sortby).click()

    def click_clear_selected_filter(self, name):
        self.search_page.selected_filter_tag(name).click()

    def click_clear_filters(self):
        self.search_page.clear_filters().click()

    def verify_the_search_bar_has_value(self, query):
        search_bar = self.search_page.search_bar()

        assert search_bar.get_attribute("value") == query

    def verify_subject_area_selected(self, subject_area):
        selected_subject_area = self.search_page.get_selected_subject_area().text
        assert selected_subject_area == subject_area

    def verify_unselected_subject_area(self):
        selected_subject_area = self.search_page.get_selected_subject_area().text
        assert selected_subject_area == "All subject areas"

    def verify_selected_filters_shown(self, subject_areas):
        actual = {i.text for i in self.search_page.selected_filter_tags()}
        expected = set(subject_areas)

        assert actual == expected

    def verify_page(self, expected):
        current_page = self.search_page.current_page()
        assert current_page.text == expected

    def click_next_page(self):
        self.search_page.next_page().click()

    def click_previous_page(self):
        self.search_page.previous_page().click()

    def verify_sort_selected(self, expected):
        value = self.search_page.checked_sort_option().get_attribute("value") or ""
        assert value == expected.lower()
