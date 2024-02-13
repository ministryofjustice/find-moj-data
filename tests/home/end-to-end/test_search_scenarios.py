from typing import Protocol

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement


class HasSelenium(Protocol):
    @property
    def selenium(self) -> RemoteWebDriver: ...


class LayoutHelpers:
    def primary_heading(self: HasSelenium):
        return self.selenium.find_element(By.TAG_NAME, "h1")

    def secondary_heading(self: HasSelenium):
        return self.selenium.find_element(By.TAG_NAME, "h2")

    @property
    def title(self: HasSelenium):
        return self.selenium.title


class HomePage:
    def search_nav_link(self: HasSelenium) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Search")


class SearchResultWrapper:
    def __init__(self, element: WebElement):
        self.element = element

    def __getattr__(self, name):
        return getattr(self.element, name)

    def link(self):
        return self.element.find_element(By.CSS_SELECTOR, "h3 a")


class SearchPage:
    def result_count(self: HasSelenium) -> WebElement:
        return self.selenium.find_element(By.ID, "result-count")

    def first_search_result(self: HasSelenium) -> SearchResultWrapper:
        return SearchResultWrapper(
            self.selenium.find_element(By.ID, "search-results").find_element(
                By.CSS_SELECTOR, ".govuk-grid-row"
            )
        )

    def search_bar(self: HasSelenium) -> WebElement:
        return self.selenium.find_element(By.NAME, "query")

    def checked_domain_checkboxes(self: HasSelenium) -> list[WebElement]:
        return self.selenium.find_elements(
            By.CSS_SELECTOR, "input:checked[name='domains']"
        )

    def domain_label(self: HasSelenium, name) -> WebElement:
        return self.selenium.find_element(By.XPATH, f"//label[ text() = '{name}' ]")

    def selected_filter_tags(self: HasSelenium) -> list[WebElement]:
        return self.selenium.find_elements(
            By.CSS_SELECTOR, ".moj-filter__tag [data-test-id='selected-domain-label']"
        )

    def apply_filters_button(self: HasSelenium):
        return self.selenium.find_element(
            By.CSS_SELECTOR, 'button[data-test-id="apply-filters"]'
        )


class TestSearchWithoutJavascriptAndCss(
    LiveServerTestCase, HomePage, SearchPage, LayoutHelpers
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        self.assertIn("Data catalogue", self.title)

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search")
        self.assertIn("Search", self.title)

    def click_on_the_search_button(self):
        self.search_nav_link().click()

    def verify_i_am_on_the_search_page(self):
        self.assertIn("Search", self.selenium.title)
        self.assertIn("Find MOJ Data", self.primary_heading().text)

    def verify_i_have_results(self):
        result_count = self.result_count().text
        self.assertRegex(result_count, r"[1-9]\d* Results")

    def click_on_the_first_result(self):
        first_result = self.first_search_result()
        self.assertTrue(first_result.text)

        first_link = first_result.link()
        item_name = first_link.text
        first_link.click()
        return item_name

    def verify_i_am_on_the_details_page(self, item_name):
        self.assertIn(item_name, self.title)
        secondary_heading_text = self.secondary_heading().text
        self.assertEquals(secondary_heading_text, item_name)

    def enter_a_query_and_submit(self, query):
        search_bar = self.search_bar()
        search_bar.send_keys(query)
        search_bar.send_keys(Keys.ENTER)

    def select_domain(self, domains):
        for domain in domains:
            self.domain_label(domain).click()

    def click_apply_filters(self):
        self.apply_filters_button().click()

    def verify_the_search_bar_has_value(self, query):
        search_bar = self.search_bar()
        self.assertEquals(search_bar.get_attribute("value"), query)

    def verify_domain_selected(self, domains):
        expected = set(domains)
        checkboxes = self.checked_domain_checkboxes()
        actual = set()
        for checkbox in checkboxes:
            value = checkbox.get_attribute("value") or ""
            actual.add(value.replace("urn:li:domain:", ""))

        self.assertEquals(actual, expected)

    def verify_selected_filters_shown(self, domains):
        actual = {i.text for i in self.selected_filter_tags()}
        expected = set(domains)
        self.assertEquals(actual, expected)

    def test_browse_to_first_item(self):
        """
        TODO: incorporate screenshots for debugging
        Convert to pytest
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
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("nomis")
        self.verify_i_am_on_the_search_page()
        self.verify_the_search_bar_has_value("nomis")
        self.verify_i_have_results()

    def test_apply_domain_filters(self):
        self.start_on_the_search_page()
        self.select_domain(["HMCTS", "HMPPS"])
        self.click_apply_filters()
        self.verify_i_am_on_the_search_page()
        self.verify_i_have_results()
        self.verify_domain_selected(["HMCTS", "HMPPS"])
        self.verify_selected_filters_shown(["HMCTS", "HMPPS"])
