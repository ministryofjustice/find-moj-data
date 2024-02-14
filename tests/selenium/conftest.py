from pathlib import Path
from typing import Any, Generator

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement

TMP_DIR = Path(__file__).parent / "../../tmp"


@pytest.fixture(scope="session")
def selenium(live_server) -> Generator[RemoteWebDriver, Any, None]:
    selenium = WebDriver()
    selenium.implicitly_wait(10)
    yield selenium
    selenium.quit()


@pytest.fixture
def screenshotter(request, selenium: RemoteWebDriver):
    counter = 1
    testname = request.node.name
    test_dir = TMP_DIR / testname
    test_dir.mkdir(parents=True, exist_ok=True)

    def screenshot(name="screenshot"):
        nonlocal counter
        body = selenium.find_element(By.TAG_NAME, "body")
        body.screenshot(str(test_dir / f"{counter}-{name}.png"))
        counter += 1

    yield screenshot


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
