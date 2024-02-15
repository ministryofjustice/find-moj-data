from pytest import CollectReport, StashKey
import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement

TMP_DIR = Path(__file__).parent / "../../tmp"


@pytest.fixture(scope="session")
def selenium(live_server) -> Generator[RemoteWebDriver, Any, None]:
    options = ChromeOptions()
    options.add_argument("headless")
    options.add_argument("window-size=1280,720")
    selenium = WebDriver(options=options)
    selenium.implicitly_wait(10)
    yield selenium
    selenium.quit()


phase_report_key = StashKey[dict[str, CollectReport]]()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    rep = yield

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep

    return rep


@pytest.fixture(autouse=True)
def screenshotter(request, selenium: RemoteWebDriver):
    yield

    testname = request.node.name
    report = request.node.stash[phase_report_key]

    if report["setup"].failed:
        # Nothing to screenshot
        pass

    elif ("call" not in report) or report["call"].failed:
        timestamp = datetime.datetime.now().strftime(r"%Y%m%d%H%M%S")
        path = str(TMP_DIR / f"{timestamp}-{testname}-failed.png")
        total_height = selenium.execute_script(
            "return document.body.parentNode.scrollHeight"
        )
        selenium.set_window_size(1920, total_height)
        selenium.save_screenshot(path)
        print(f"Screenshot saved to {path}")


class Page:
    def __init__(self, selenium):
        self.selenium = selenium


class DetailsPage(Page):
    def secondary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h2")


class HomePage(Page):

    def search_nav_link(self) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Search")


class SearchResultWrapper:
    def __init__(self, element: WebElement):
        self.element = element

    def __getattr__(self, name):
        return getattr(self.element, name)

    def link(self):
        return self.element.find_element(By.CSS_SELECTOR, "h3 a")


class SearchPage(Page):

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
