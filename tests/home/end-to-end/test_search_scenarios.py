from typing import Protocol

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.common.by import By
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

    def test_browse_to_first_item(self):
        """
        TODO: incorporate screenshots for debugging
        Convert to pytest
        Tag the test so it doesn't slow down the main CI job
        Factor out steps
        """
        # Navigate to search page
        self.selenium.get(f"{self.live_server_url}")
        self.assertIn("Data catalogue", self.selenium.title)

        self.search_nav_link().click()
        self.assertIn("Search", self.selenium.title)
        self.assertIn("Find MOJ Data", self.primary_heading().text)

        # Read number of results
        result_count = self.result_count().text
        self.assertRegex(result_count, r"\d+ Results")

        # Read first result
        first_result = self.first_search_result()
        self.assertTrue(first_result.text)

        # Click the link
        first_link = first_result.link()
        item_name = first_link.text
        first_link.click()

        # Verify we are on the details page
        self.assertIn(item_name, self.title)
        secondary_heading_text = self.secondary_heading().text
        self.assertEquals(secondary_heading_text, item_name)
