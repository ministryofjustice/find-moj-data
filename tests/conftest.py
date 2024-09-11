from datetime import datetime, timezone
from pathlib import Path
from random import choice
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from data_platform_catalogue.client.datahub_client import DataHubCatalogueClient
from data_platform_catalogue.entities import (
    Chart,
    Column,
    ColumnRef,
    CustomEntityProperties,
    Dashboard,
    Database,
    DomainRef,
    EntityRef,
    EntitySummary,
    GlossaryTermRef,
    Governance,
    OwnerRef,
    RelationshipType,
    Table,
    TagRef,
)
from data_platform_catalogue.search_types import (
    DomainOption,
    FacetOption,
    ResultType,
    SearchFacets,
    SearchResponse,
    SearchResult,
)
from django.conf import settings
from django.test import Client
from faker import Faker
from pytest import CollectReport, StashKey
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from home.forms.search import SearchForm
from home.models.domain_model import DomainModel
from home.service.details import DatabaseDetailsService
from home.service.domain_fetcher import DomainFetcher
from home.service.search import SearchService
from home.service.search_facet_fetcher import SearchFacetFetcher
from home.service.search_tag_fetcher import SearchTagFetcher

TMP_DIR = (Path(__file__).parent / "tmp").resolve()

fake = Faker()


def pytest_addoption(parser):
    parser.addoption("--chromedriver-path", action="store")
    parser.addoption("--axe-version", action="store")


@pytest.fixture(autouse=True, scope="session")
def remove_azure_auth_middleware():
    auth_middleware = "azure_auth.middleware.AzureMiddleware"
    if auth_middleware in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove(auth_middleware)


@pytest.fixture
def chromedriver_path(request):
    return request.config.getoption("--chromedriver-path")


@pytest.fixture
def axe_version(request):
    return request.config.getoption("--axe-version") or "latest"


@pytest.fixture(scope="function")
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
        timestamp = datetime.now().strftime(r"%Y%m%d%H%M%S")
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

    def primary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h1")


class DetailsPage(Page):
    def request_access(self):
        return self.selenium.find_element(By.ID, "request_access")

    def contact_channels(self):
        return self.selenium.find_element(By.ID, "contact_channels")

    def data_owner(self):
        return self.selenium.find_element(By.ID, "data_owner")


class DatabaseDetailsPage(DetailsPage):
    def primary_heading(self):
        return self.selenium.find_element(By.TAG_NAME, "h1")

    def database_details(self):
        return self.selenium.find_element(By.ID, "metadata-property-list")

    def database_tables(self):
        return self.selenium.find_element(By.TAG_NAME, "table")

    def table_link(self):
        return self.selenium.find_element(
            By.CSS_SELECTOR, ".govuk-table tr td:first-child a"
        )


class TableDetailsPage(DetailsPage):
    def column_descriptions(self):
        return [
            c.text
            for c in self.selenium.find_elements(By.CSS_SELECTOR, ".column-description")
        ]


class HomePage(Page):
    def search_nav_link(self) -> WebElement:
        return self.selenium.find_element(By.LINK_TEXT, "Search")

    def search_bar(self) -> WebElement:
        return self.selenium.find_element(By.NAME, "query")

    def domain_link(self, domain) -> WebElement:
        all_domains = self.selenium.find_elements(
            By.CSS_SELECTOR, "ul#domain-list li a"
        )
        all_domain_names = [d.text for d in all_domains]
        result = next(
            (d for d in all_domains if domain == d.text.split("(")[0].strip()), None
        )
        if not result:
            raise Exception(f"{domain!r} not found in {all_domain_names!r}")
        return result


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
def page_titles():
    pages = [
        "Home",
        "Search MoJ data",
    ]
    return [f"{page} - Find MOJ data - GOV.UK" for page in pages]


def generate_search_result(
    result_type: ResultType | None = None, urn=None, metadata=None
) -> SearchResult:
    """
    Generate a random search result
    """
    name = fake.name()

    return SearchResult(
        urn=urn or fake.unique.name(),
        result_type=(
            choice((ResultType.DATABASE, ResultType.TABLE))
            if result_type is None
            else result_type
        ),
        name=name,
        fully_qualified_name=name,
        description=fake.paragraph(),
        metadata=metadata or {"search_summary": "a"},
    )


def search_result_from_database(database: Database):
    return SearchResult(
        urn=database.urn or "",
        result_type=ResultType.DATABASE,
        name=database.name,
        fully_qualified_name=database.fully_qualified_name or "",
        description=database.description,
        metadata={},
    )


def generate_table_metadata(
    name: str = fake.unique.name(),
    description: str = fake.unique.paragraph(),
    relations=None,
    custom_properties=None,
) -> Table:
    """
    Generate a fake table metadata object
    """
    return Table(
        urn="urn:li:Dataset:fake",
        display_name=f"Foo.{name}",
        name=name,
        fully_qualified_name=f"Foo.{name}",
        description=description,
        relationships=relations
        or {RelationshipType.PARENT: [], RelationshipType.DATA_LINEAGE: []},
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        glossary_terms=[
            GlossaryTermRef(
                display_name="some-term",
                urn="urn:li:glossaryTerm:Entity",
                description="some description",
            )
        ],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        column_details=[
            Column(
                name="urn",
                display_name="urn",
                type="string",
                description="description **with markdown**",
                nullable=False,
                is_primary_key=True,
                foreign_keys=[
                    ColumnRef(
                        name="urn",
                        display_name="urn",
                        table=EntityRef(
                            urn="urn:li:dataset:(urn:li:dataPlatform:datahub,Dataset,PROD)",
                            display_name="Dataset",
                        ),
                    )
                ],
            ),
        ],
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=custom_properties or CustomEntityProperties(),
    )


def generate_chart_metadata(
    name: str = fake.unique.name(),
    description: str = fake.unique.paragraph(),
    relations=None,
    custom_properties=None,
) -> Chart:
    """
    Generate a fake database metadata object
    """
    return Chart(
        urn="urn:li:container:fake",
        external_url="https://data.justice.gov.uk/prisons/public-protection/absconds",
        display_name=f"Foo.{name}",
        name=name,
        fully_qualified_name=f"Foo.{name}",
        description=description,
        relationships=relations or {RelationshipType.PARENT: []},
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        glossary_terms=[
            GlossaryTermRef(
                display_name="some-term",
                urn="urn:li:glossaryTerm:Entity",
                description="some description",
            )
        ],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=custom_properties or CustomEntityProperties(),
    )


def generate_database_metadata(
    name: str = fake.unique.name(),
    description: str = fake.unique.paragraph(),
    relations=None,
    custom_properties=None,
) -> Database:
    """
    Generate a fake database metadata object
    """
    return Database(
        urn="urn:li:container:fake",
        display_name=f"Foo.{name}",
        name=name,
        fully_qualified_name=f"Foo.{name}",
        description=description,
        relationships=relations
        or {
            RelationshipType.CHILD: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:dataset:fake_table", display_name="fake_table"
                    ),
                    description="table description",
                    tags=[
                        TagRef(
                            display_name="some-tag",
                            urn="urn:li:tag:dc_display_in_catalogue",
                        )
                    ],
                    entity_type="TABLE",
                )
            ]
        },
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        glossary_terms=[
            GlossaryTermRef(
                display_name="some-term",
                urn="urn:li:glossaryTerm:Entity",
                description="some description",
            )
        ],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=custom_properties or CustomEntityProperties(),
    )


def generate_dashboard_metadata(
    name: str = fake.unique.name(),
    description: str = fake.unique.paragraph(),
    relations=None,
    custom_properties=None,
) -> Dashboard:
    """
    Generate a fake database metadata object
    """
    return Dashboard(
        urn="urn:li:dashboard:fake",
        display_name=f"Foo.{name}",
        name=name,
        fully_qualified_name=f"Foo.{name}",
        description=description,
        relationships=relations
        or {
            RelationshipType.CHILD: [
                EntitySummary(
                    entity_ref=EntityRef(
                        urn="urn:li:chart:fake_chart", display_name="fake_chart"
                    ),
                    description="chart description",
                    tags=[
                        TagRef(
                            display_name="some-tag",
                            urn="urn:li:tag:dc_display_in_catalogue",
                        )
                    ],
                    entity_type="CHART",
                )
            ]
        },
        external_url="www.a-great-exmaple-dashboard.com",
        domain=DomainRef(display_name="LAA", urn="LAA"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name="", email="Contact email for the user", urn=""
            ),
            data_stewards=[
                OwnerRef(display_name="", email="Contact email for the user", urn="")
            ],
        ),
        tags=[TagRef(display_name="some-tag", urn="urn:li:tag:Entity")],
        glossary_terms=[
            GlossaryTermRef(
                display_name="some-term",
                urn="urn:li:glossaryTerm:Entity",
                description="some description",
            )
        ],
        last_modified=datetime(2024, 3, 5, 6, 16, 47, 814000, tzinfo=timezone.utc),
        created=None,
        platform=EntityRef(urn="urn:li:dataPlatform:athena", display_name="athena"),
        custom_properties=custom_properties or CustomEntityProperties(),
    )


@pytest.fixture(autouse=True)
def example_database(name="example_database"):
    return generate_database_metadata(name=name)


@pytest.fixture(autouse=True)
def example_dashboard(name="example_dashboard"):
    return generate_dashboard_metadata(name=name)


def generate_page(page_size=20, result_type: ResultType | None = None):
    """
    Generate a fake search page
    """
    results = []
    for _ in range(page_size):
        results.append(generate_search_result(result_type=result_type))
    return results


@pytest.fixture(autouse=True)
def client():
    client = Client()
    return client


@pytest.fixture(autouse=True)
def mock_catalogue(request, example_database, example_dashboard):
    if "datahub" in request.keywords:
        yield None
        return

    patcher = patch("home.service.base.GenericService._get_catalogue_client")
    mock_fn = patcher.start()
    mock_catalogue = MagicMock(spec=DataHubCatalogueClient)
    mock_fn.return_value = mock_catalogue
    mock_search_response(
        mock_catalogue, page_results=generate_page(), total_results=100
    )
    mock_list_domains_response(
        mock_catalogue,
        domains=[
            DomainOption(
                urn="urn:li:domain:prisons",
                name="Prisons",
                total=fake.random_int(min=1, max=100),
            ),
            DomainOption(
                urn="urn:li:domain:courts",
                name="Courts",
                total=fake.random_int(min=1, max=100),
            ),
            DomainOption(
                urn="urn:li:domain:finance",
                name="Finance",
                total=fake.random_int(min=1, max=100),
            ),
            DomainOption(
                urn="urn:li:domain:hq",
                name="HQ",
                total=0,
            ),
        ],
    )
    mock_search_facets_response(
        mock_catalogue,
        domains=[
            FacetOption(
                value="urn:li:domain:prisons",
                label="Prisons",
                count=fake.random_int(min=0, max=100),
            ),
            FacetOption(
                value="urn:li:domain:courts",
                label="Courts",
                count=fake.random_int(min=0, max=100),
            ),
            FacetOption(
                value="urn:li:domain:finance",
                label="Finance",
                count=fake.random_int(min=0, max=100),
            ),
        ],
    )
    mock_get_glossary_terms_response(mock_catalogue)
    mock_get_chart_details_response(mock_catalogue)
    mock_get_table_details_response(mock_catalogue)
    mock_get_database_details_response(mock_catalogue, example_database)
    mock_get_dashboard_details_response(mock_catalogue, example_dashboard)
    mock_get_tags_response(mock_catalogue)

    yield mock_catalogue

    patcher.stop()


def mock_list_database_tables_response(mock_catalogue, total_results, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.list_database_tables.return_value = search_response


def mock_get_chart_details_response(mock_catalogue):
    mock_catalogue.get_chart_details.return_value = generate_chart_metadata()


def mock_get_table_details_response(mock_catalogue):
    mock_catalogue.get_table_details.return_value = generate_table_metadata()


def mock_get_dashboard_details_response(mock_catalogue, example_dashboard):
    mock_catalogue.get_dashboard_details.return_value = example_dashboard


def mock_get_database_details_response(mock_catalogue, example_database):
    mock_catalogue.get_database_details.return_value = example_database


def mock_search_response(mock_catalogue, total_results=0, page_results=()):
    search_response = SearchResponse(
        total_results=total_results, page_results=page_results
    )
    mock_catalogue.search.return_value = search_response


def mock_list_domains_response(mock_catalogue, domains):
    mock_catalogue.list_domains.return_value = domains


def mock_search_facets_response(mock_catalogue, domains):
    mock_catalogue.search_facets.return_value = SearchFacets({"domains": domains})


def mock_get_tags_response(mock_catalogue):
    mock_catalogue.get_tags.return_value = [
        ("tag-1", "urn:li:tag:tag-1"),
        ("tag-2", "urn:li:tag:tag-2"),
        ("tag-3", "urn:li:tag:tag-3"),
    ]


def mock_get_glossary_terms_response(mock_catalogue):
    mock_catalogue.get_glossary_terms.return_value = SearchResponse(
        total_results=3,
        page_results=[
            SearchResult(
                urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                name="IAO",
                description="Information asset owner.\n",
                metadata={
                    "parentNodes": [
                        {
                            "properties": {
                                "name": "Data protection terms",
                                "description": "Data protection terms",
                            }
                        }
                    ]
                },
                result_type=ResultType.GLOSSARY_TERM,
            ),
            SearchResult(
                urn="urn:li:glossaryTerm:022b9b68-c211-47ae-aef0-2db13acfeca8",
                name="Other term",
                description="Term description to test groupings work",
                metadata={
                    "parentNodes": [
                        {
                            "properties": {
                                "name": "Data protection terms",
                                "description": "Data protection terms",
                            }
                        }
                    ]
                },
                result_type=ResultType.GLOSSARY_TERM,
            ),
            SearchResult(
                urn="urn:li:glossaryTerm:0eb7af28-62b4-4149-a6fa-72a8f1fea1e6",
                name="Security classification",
                description="Only data that is 'official'",
                metadata={"parentNodes": []},
                result_type=ResultType.GLOSSARY_TERM,
            ),
        ],
    )


@pytest.fixture
def search_facets():
    return SearchFacetFetcher().fetch()


@pytest.fixture
def list_domains(filter_zero_entities):
    return DomainFetcher(filter_zero_entities).fetch()


@pytest.fixture
def search_tags():
    return SearchTagFetcher().fetch()


@pytest.fixture
def valid_domain():
    domains = DomainFetcher().fetch()
    return DomainModel(
        domains,
    ).top_level_domains[0]


@pytest.fixture
def valid_form(valid_domain):
    valid_form = SearchForm(
        data={
            "query": "test",
            "domain": valid_domain.urn,
            "entity_types": ["TABLE"],
            "where_to_access": ["analytical_platform"],
            "sort": "ascending",
            "clear_filter": False,
            "clear_label": False,
            "tags": ["tag-1"],
        }
    )
    assert valid_form.is_valid()

    return valid_form


@pytest.fixture
def search_service(valid_form):
    return SearchService(form=valid_form, page="1")


@pytest.fixture
def search_context(search_service):
    return search_service.context


@pytest.fixture
def detail_database_context(mock_catalogue):
    mock_catalogue.search.return_value = SearchResponse(
        total_results=1,
        page_results=generate_page(page_size=1, result_type=ResultType.DATABASE),
    )

    details_service = DatabaseDetailsService(urn="urn:li:container:test")
    context = details_service._get_context()
    return context


@pytest.fixture
def dataset_with_parent(mock_catalogue) -> dict[str, Any]:
    """
    Mock the catalogue response for a dataset that has a parent
    """
    container = {"urn": "database-abc", "name": "parent"}

    table_metadata = generate_table_metadata()
    mock_catalogue.get_table_details.return_value = table_metadata

    mock_catalogue.search.return_value = SearchResponse(
        total_results=1,
        page_results=[
            generate_search_result(
                result_type=ResultType.TABLE,
                urn="table-abc",
                metadata={},
            )
        ],
    )

    return {
        "urn": "dataset-abc",
        "parent_entity": container,
        "table_metadata": table_metadata,
    }


@pytest.fixture(scope="function")
def set_redis_cache_env(monkeypatch):
    monkeypatch.setenv("REDIS_AUTH_TOKEN", "testredistoken")
    monkeypatch.setenv(
        "REDIS_PRIMARY_ENDPOINT_ADDRESS",
        "master.cp-12345.iwfvzo.euw2.cache.amazonaws.com",
    )
    monkeypatch.setenv(
        "REDIS_MEMBER_CLUSTERS",
        '["cp-f05ff2dca7d81952-001", "cp-f05ff2dca7d81952-002"]',
    )


@pytest.fixture(scope="function")
def unset_redis_cache_env(monkeypatch):
    monkeypatch.delenv("REDIS_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("REDIS_PRIMARY_ENDPOINT_ADDRESS", raising=False)
    monkeypatch.delenv("REDIS_MEMBER_CLUSTERS", raising=False)
