import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
from pytest import CollectReport, StashKey
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

TMP_DIR = (Path(__file__).parent / "../../tmp").resolve()


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
        TMP_DIR.mkdir(exist_ok=True)
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


class DatabaseDetailsPage(Page):
    def primary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h1")

    def secondary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h2")

    def database_details(self):
        return self.selenium.find_element(By.ID, "metadata-property-list")

    def database_tables(self):
        return self.selenium.find_element(By.TAG_NAME, "table")

    def table_link(self):
        return self.selenium.find_element(By.LINK_TEXT, "Table details")


class TableDetailsPage(Page):
    def caption(self):
        return self.selenium.find_element(By.CSS_SELECTOR, ".govuk-caption-m").text

    def column_descriptions(self):
        return [
            c.text
            for c in self.selenium.find_elements(By.CSS_SELECTOR, ".column-description")
        ]


class HomePage(Page):
    def search_nav_link(self) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Search")

    def glossary_nav_link(self) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Glossary")


class GlossaryPage(Page):
    def primary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h1")


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

    def domain_select(self) -> WebElement:
        return Select(self.selenium.find_element(By.ID, "id_domain"))

    def subdomain_select(self) -> WebElement:
        return Select(self.selenium.find_element(By.ID, "id_subdomain"))

    def select_domain(self, domain) -> WebElement:
        select = self.domain_select()
        return select.select_by_visible_text(domain)

    def select_subdomain(self, domain) -> WebElement:
        select = self.subdomain_select()
        print(f"Selecting subdomain {domain}")
        return select.select_by_visible_text(domain)

    def get_selected_domain(self) -> WebElement:
        select = self.domain_select()
        return select.first_selected_option

    def get_selected_subdomain(self) -> WebElement:
        select = self.subdomain_select()
        return select.first_selected_option

    def get_all_filter_names(self) -> list:
        filter_names = [
            item.text
            for item in self.selenium.find_elements(
                By.CLASS_NAME, "govuk-checkboxes__item"
            )
        ]
        return filter_names

    def get_selected_checkbox_filter_names(self) -> list:
        selected_filters = [
            item.accessible_name
            for item in self.selenium.find_elements(By.TAG_NAME, "input")
            if item.aria_role == "checkbox" and item.is_selected()
        ]
        return selected_filters

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
def details_database_page(selenium) -> DatabaseDetailsPage:
    return DatabaseDetailsPage(selenium)


@pytest.fixture
def table_details_page(selenium) -> TableDetailsPage:
    return TableDetailsPage(selenium)


@pytest.fixture
def glossary_page(selenium) -> GlossaryPage:
    return GlossaryPage(selenium)


@pytest.fixture
def page_titles():
    pages = ["Home", "Search", "Details", "Glossary"]
    return [f"{page} - Find MOJ data - GOV.UK" for page in pages]
