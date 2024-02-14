import re
import subprocess
from typing import Protocol

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement


@pytest.fixture(scope="module")
def selenium(live_server):
    selenium = WebDriver()
    selenium.implicitly_wait(10)
    yield selenium
    selenium.quit()


class DetailsPage:
    def __init__(self, selenium):
        self.selenium = selenium

    def secondary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h2")


class HomePage:
    def __init__(self, selenium):
        self.selenium = selenium

    def search_nav_link(self) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Search")


class SearchResultWrapper:
    def __init__(self, element: WebElement):
        self.element = element

    def __getattr__(self, name):
        return getattr(self.element, name)

    def link(self):
        return self.element.find_element(By.CSS_SELECTOR, "h3 a")


class SearchPage:
    def __init__(self, selenium):
        self.selenium = selenium

    def primary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h1")

    def result_count(self) -> WebElement:
        return self.selenium.find_element(By.ID, "result-count")

    def first_search_result(self) -> SearchResultWrapper:
        return SearchResultWrapper(
            self.selenium.find_element(By.ID, "search-results").find_element(
                By.CSS_SELECTOR, ".govuk-grid-row"
            )
        )

    def search_bar(self) -> WebElement:
        return self.selenium.find_element(By.NAME, "query")

    def search_button(self) -> WebElement:
        return self.selenium.find_element(By.CLASS_NAME, "search-button")

    def checked_domain_checkboxes(self) -> list[WebElement]:
        return self.selenium.find_elements(
            By.CSS_SELECTOR, "input:checked[name='domains']"
        )

    def checked_sort_option(self) -> WebElement:
        return self.selenium.find_element(By.CSS_SELECTOR, "input:checked[name='sort']")

    def domain_label(self, name) -> WebElement:
        return self.selenium.find_element(By.XPATH, f"//label[ text() = '{name}' ]")

    def sort_label(self, name) -> WebElement:
        return self.selenium.find_element(By.XPATH, f"//label[ text() = '{name}' ]")

    def selected_filter_tags(self) -> list[WebElement]:
        return self.selenium.find_elements(
            By.CSS_SELECTOR, ".moj-filter__tag [data-test-id='selected-domain-label']"
        )

    def selected_filter_tag(self, value) -> WebElement:
        for result in self.selenium.find_elements(
            By.CSS_SELECTOR, ".moj-filter__tag [data-test-id='selected-domain-label']"
        ):
            if result.text == value:
                return result

        raise Exception(f"No selected filter with text {value}")

    def clear_filters(self) -> WebElement:
        return self.selenium.find_element(By.ID, "clear_filter")

    def apply_filters_button(self) -> WebElement:
        return self.selenium.find_element(
            By.CSS_SELECTOR, 'button[data-test-id="apply-filters"]'
        )

    def current_page(self) -> WebElement:
        return self.selenium.find_element(
            By.CLASS_NAME, "govuk-pagination__item--current"
        )

    def next_page(self) -> WebElement:
        return self.selenium.find_element(
            By.CLASS_NAME, "govuk-pagination__next"
        ).find_element(By.TAG_NAME, "a")

    def previous_page(self) -> WebElement:
        return self.selenium.find_element(
            By.CLASS_NAME, "govuk-pagination__prev"
        ).find_element(By.TAG_NAME, "a")


@pytest.fixture
def home_page(selenium) -> HomePage:
    return HomePage(selenium)


@pytest.fixture
def search_page(selenium) -> SearchPage:
    return SearchPage(selenium)


@pytest.fixture
def details_page(selenium) -> DetailsPage:
    return DetailsPage(selenium)


class TestSearchWithoutJavascriptAndCss:
    """
    Test interacting with the search form through the browser,
    as a user would
    """

    def check_for_accessibility_issues(self):
        command = ["npx", "@axe-core/cli", "-q", self.selenium.current_url]
        output = subprocess.run(command, capture_output=True, text=True)
        assert output.returncode == 0, output.stdout

    @pytest.fixture(autouse=True)
    def setup(self, live_server, selenium, home_page, search_page, details_page):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.search_page = search_page
        self.details_page = details_page

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert "Data catalogue" in self.selenium.title

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search?new=True")
        assert "Search" in self.selenium.title

    def click_on_the_search_button(self):
        self.home_page.search_nav_link().click()

    def verify_i_am_on_the_search_page(self):
        assert "Search" in self.selenium.title
        assert "Find MOJ Data" in self.search_page.primary_heading().text

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

        secondary_heading_text = self.details_page.secondary_heading().text

        assert secondary_heading_text == item_name

    def enter_a_query_and_submit(self, query):
        search_bar = self.search_page.search_bar()
        search_bar.send_keys(query)
        self.click_search_button()

    def select_domain(self, domains):
        for domain in domains:
            self.search_page.domain_label(domain).click()

    def click_sort_option(self, sortby):
        self.search_page.sort_label(sortby).click()

    def click_search_button(self):
        self.search_page.search_button().click()

    def click_apply_filters(self):
        self.search_page.apply_filters_button().click()

    def click_clear_selected_filter(self, name):
        self.search_page.selected_filter_tag(name).click()

    def click_clear_filters(self):
        self.search_page.clear_filters().click()

    def verify_the_search_bar_has_value(self, query):
        search_bar = self.search_page.search_bar()

        assert search_bar.get_attribute("value") == query

    def verify_domain_selected(self, domains):
        expected = set(domains)
        checkboxes = self.search_page.checked_domain_checkboxes()
        actual = set()
        for checkbox in checkboxes:
            value = checkbox.get_attribute("value") or ""
            actual.add(value.replace("urn:li:domain:", ""))

        assert actual == expected

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

    def test_browse_to_first_item(self):
        """
        Browses from the home page -> search -> details page

        TODO: incorporate screenshots for debugging
        See if we can stub out the actual catalogue
        Tag the test so it doesn't slow down the main CI job
        """
        self.start_on_the_home_page()
        self.click_on_the_search_button()
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
        self.start_on_the_search_page()
        self.select_domain(["HMCTS", "HMPPS"])
        self.click_apply_filters()
        self.verify_i_am_on_the_search_page()
        self.verify_i_have_results()
        self.verify_domain_selected(["HMCTS", "HMPPS"])
        self.verify_selected_filters_shown(["HMCTS", "HMPPS"])

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
        self.click_search_button()
        self.verify_i_have_results()
        self.verify_sort_selected("Ascending")

    def test_filters_query_and_sort_persist(self):
        self.start_on_the_search_page()
        self.select_domain(["HMCTS", "HMPPS"])
        self.click_apply_filters()
        self.enter_a_query_and_submit("nomis")
        self.click_sort_option("Ascending")
        self.click_search_button()

        self.verify_i_have_results()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_domain_selected(["HMCTS", "HMPPS"])
        self.verify_sort_selected("Ascending")

    def test_adding_a_query_resets_pagination(self):
        self.start_on_the_search_page()
        self.click_next_page()
        self.verify_page("2")
        self.enter_a_query_and_submit("nomis")
        self.verify_page("1")

    def test_adding_a_filter_resets_pagination(self):
        self.start_on_the_search_page()
        self.click_next_page()
        self.verify_page("2")

        self.select_domain(["HMPPS"])
        self.click_apply_filters()
        self.verify_page("1")

    def test_clear_single_filter(self):
        self.start_on_the_search_page()
        self.select_domain(["HMPPS", "HMCTS"])
        self.click_apply_filters()
        self.click_clear_selected_filter("HMPPS")

        self.verify_domain_selected(["HMCTS"])

    def test_clear_all_filters(self):
        self.start_on_the_search_page()
        self.select_domain(["HMPPS", "HMCTS"])
        self.click_apply_filters()
        self.click_clear_filters()

        self.verify_domain_selected([])

    def test_automated_accessibility_home(self):
        self.start_on_the_home_page()
        self.check_for_accessibility_issues()

    def test_automated_accessibility_search(self):
        self.start_on_the_search_page()
        self.check_for_accessibility_issues()
