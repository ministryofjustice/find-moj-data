import re

import pytest
from data_platform_catalogue.search_types import ResultType

from tests.conftest import generate_page, mock_search_response

from .helpers import check_for_accessibility_issues


@pytest.mark.slow
class TestSearch:
    """
    Test interacting with the search form through the browser,
    as a user would
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        home_page,
        search_page,
        details_data_product_page,
        chromedriver_path,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.search_page = search_page
        self.details_data_product_page = details_data_product_page
        self.chromedriver_path = chromedriver_path

    def verify_glossary_link_from_homepage_works(self):
        self.start_on_the_home_page()
        self.click_on_the_glossary_link()
        self.verify_i_am_on_the_glossary_page()

    def test_browse_to_first_item_data_product(self, mock_catalogue):
        """
        Browses from the home page -> search -> details page
        """
        # we need to mock search response to be data products
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=generate_page(result_type=ResultType.DATA_PRODUCT),
            total_results=100,
        )

        self.start_on_the_home_page()
        self.click_on_the_search_link()

        self.verify_i_am_on_the_search_page()
        self.verify_i_have_results()
        item_name = self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page(item_name)

    def test_search_with_query(self):
        """
        Types a search query and press enter
        """
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("nomis")
        self.verify_i_am_on_the_search_page()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_i_have_results()

    def test_apply_domain_filters(self):
        """
        Interacts with the filters on the left hand side
        """
        domain = "HMPPS"
        subdomain = "Prisons"
        self.start_on_the_search_page()
        self.select_domain(domain)
        self.select_subdomain(subdomain)
        self.click_apply_filters()
        self.verify_i_am_on_the_search_page()
        self.verify_i_have_results()
        self.verify_domain_selected(domain)
        self.verify_subdomain_selected(subdomain)

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

    def test_sorting(self):
        """
        Interact with the sort control. Note: without javascript, this requires
        the form to be submitted by pressing a button.
        """
        self.start_on_the_search_page()

        # FIXME: this isn't preselected if the `new` query param is missing
        self.verify_sort_selected("Relevance")

        self.click_sort_option("Ascending")
        self.click_on_the_search_button()
        self.verify_i_have_results()
        self.verify_sort_selected("Ascending")

    def test_filters_query_and_sort_persist(self):
        """
        Search settings persist as the user continues to
        interact with the search page.
        """
        domain = "HMPPS"
        subdomain = "Prisons"
        self.start_on_the_search_page()
        self.select_domain(domain)
        self.select_subdomain(subdomain)
        self.click_apply_filters()
        self.enter_a_query_and_submit("nomis")
        self.click_sort_option("Ascending")
        self.click_on_the_search_button()

        self.verify_i_have_results()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_domain_selected(domain)
        self.verify_subdomain_selected(subdomain)
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

        self.select_domain("HMPPS")
        self.click_apply_filters()
        self.verify_page("1")

    def test_clear_single_filter(self):
        """
        Users can clear a filter by clicking on it within the "selected filters"
        panel.
        """
        domain = "HMPPS"
        self.start_on_the_search_page()
        self.select_domain(domain)
        self.click_apply_filters()
        self.verify_domain_selected(domain)
        self.click_clear_selected_filter(domain)
        self.verify_unselected_domain()
        self.verify_unselected_subdomain()

    def test_clear_all_filters(self):
        """
        Users can click a button to clear all filters.
        """
        domain = "HMCTS"
        self.start_on_the_search_page()
        self.select_domain(domain)
        self.click_apply_filters()
        self.verify_domain_selected(domain)
        self.click_clear_filters()
        self.verify_unselected_domain()

    def test_automated_accessibility_home(self):
        self.start_on_the_home_page()
        check_for_accessibility_issues(
            self.selenium.current_url, chromedriver_path=self.chromedriver_path
        )

    def test_automated_accessibility_search(self):
        self.start_on_the_search_page()
        check_for_accessibility_issues(
            self.selenium.current_url, chromedriver_path=self.chromedriver_path
        )

    def test_search_to_data_product_details(self, mock_catalogue):
        """
        Users can search a data product and got to its details page
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=generate_page(result_type=ResultType.DATA_PRODUCT),
            total_results=100,
        )
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        item_name = self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page(item_name)
        self.verify_data_product_details()
        self.verify_data_product_tables_listed()

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert "Data catalogue" in self.selenium.title

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search?new=True")
        assert "Search" in self.selenium.title

    def click_on_the_search_link(self):
        self.home_page.search_nav_link().click()

    def click_on_the_glossary_link(self):
        self.home_page.glossary_nav_link().click()

    def click_on_the_search_button(self):
        self.search_page.search_button().click()

    def verify_i_am_on_the_search_page(self):
        assert "Search" in self.selenium.title
        assert "Find MOJ Data" in self.search_page.primary_heading().text

    def verify_i_am_on_the_glossary_page(self):
        assert "Glossary" in self.selenium.title

    def verify_i_have_results(self):
        result_count = self.search_page.result_count().text
        assert re.match(r"[1-9]\d* Results", result_count)

    def click_on_the_first_result(self):
        first_result = self.search_page.first_search_result()
        assert first_result.text

        first_link = first_result.link()
        item_name = first_link.text
        first_link.click()
        return item_name

    def verify_i_am_on_the_details_page(self, item_name):
        assert item_name in self.selenium.title

        secondary_heading_text = self.details_data_product_page.secondary_heading().text

        assert secondary_heading_text == item_name

    def enter_a_query_and_submit(self, query):
        search_bar = self.search_page.search_bar()
        search_bar.send_keys(query)
        self.click_on_the_search_button()

    def select_domain(self, domain):
        self.search_page.select_domain(domain)

    def select_subdomain(self, domain):
        self.search_page.select_subdomain(domain)

    def click_sort_option(self, sortby):
        self.search_page.sort_label(sortby).click()

    def click_apply_filters(self):
        self.search_page.apply_filters_button().click()

    def click_clear_selected_filter(self, name):
        self.search_page.selected_filter_tag(name).click()

    def click_clear_filters(self):
        self.search_page.clear_filters().click()

    def verify_the_search_bar_has_value(self, query):
        search_bar = self.search_page.search_bar()

        assert search_bar.get_attribute("value") == query

    def verify_domain_selected(self, domain):
        selected_domain = self.search_page.get_selected_domain().text
        assert selected_domain == domain

    def verify_subdomain_selected(self, domain):
        selected_domain = self.search_page.get_selected_subdomain().text
        assert selected_domain == domain

    def verify_unselected_domain(self):
        selected_domain = self.search_page.get_selected_domain().text
        assert selected_domain == "All domains"

    def verify_unselected_subdomain(self):
        selected_domain = self.search_page.get_selected_subdomain().text
        assert selected_domain == "All subdomains"

    def verify_selected_filters_shown(self, domains):
        actual = {i.text for i in self.search_page.selected_filter_tags()}
        expected = set(domains)

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

    def verify_data_product_tables_listed(self):
        tables = self.details_data_product_page.data_product_tables()
        assert tables.text

    def verify_data_product_details(self):
        data_product_details = self.details_data_product_page.data_product_details()
        assert data_product_details.text
