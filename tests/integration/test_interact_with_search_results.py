import pytest
from selenium.webdriver.common.by import By

from datahub_client.entities import TableEntityMapping
from tests.conftest import (
    generate_page,
    generate_table_metadata,
    mock_get_table_details_response,
    mock_search_response,
    search_result_from_database,
    search_result_from_publication_collection,
    search_result_from_publication_dataset,
)


@pytest.mark.slow
class TestInteractWithSearchResults:
    """
    Given I have a performed a search
    When I click on a search result
    Then I should be able to reach the details page for a database, table, or chart
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        search_page,
        details_database_page,
        table_details_page,
        publication_collection_details_page,
        publication_dataset_details_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.search_page = search_page
        self.details_database_page = details_database_page
        self.table_details_page = table_details_page
        self.publication_collection_details_page = publication_collection_details_page
        self.publication_dataset_details_page = publication_dataset_details_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def test_table_search_to_details(self, mock_catalogue):
        """
        Users can search for a table and access a detail page
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=generate_page(result_type=TableEntityMapping),
            total_results=100,
        )
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        self.click_on_the_first_result()
        self.verify_i_am_on_the_table_details_page(
            "Description:\ndescription with markdown"
        )

    def test_table_search_to_details_accessibility(self, mock_catalogue):
        """
        Users with accessibility needs are presented with useful description info in details
        tables, e.g. for missing details of a column in a table
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=generate_page(result_type=TableEntityMapping),
            total_results=100,
        )
        table_no_column_description = generate_table_metadata(column_description="")
        mock_get_table_details_response(mock_catalogue, table_no_column_description)
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        self.click_on_the_first_result()
        self.verify_i_am_on_the_table_details_page(
            "Description:\nA description for urn does not exist"
        )

    def test_database_search_to_table_details(self, mock_catalogue, example_database):
        """
        Users can search and drill down into details
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=[search_result_from_database(example_database)],
            total_results=100,
        )
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        item_name = self.click_on_the_first_result()
        self.verify_i_am_on_the_database_details_page(item_name)
        self.verify_database_details()
        self.verify_database_tables_listed()
        self.click_on_table()
        self.verify_i_am_on_the_table_details_page(
            "Description:\ndescription with markdown"
        )

    def test_publication_collection_search_to_details(
        self, mock_catalogue, example_publication_collection
    ):
        """
        Users can search for a publication collection and access a detail page
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=[
                search_result_from_publication_collection(
                    example_publication_collection
                )
            ],
            total_results=100,
        )
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        item_name = self.click_on_the_first_result()
        self.verify_i_am_on_the_publications_collections_details_page(item_name)
        self.verify_publication_collection_details()
        self.verify_publication_collection_datasets_listed()
        self.click_on_publication_collection_dataset_link()
        self.verify_i_am_on_the_publication_dataset_details_page()

    def test_publication_dataset_search_to_details(
        self, mock_catalogue, example_publication_dataset
    ):
        """
        Users can search for a publication dataset and access a detail page
        """
        mock_search_response(
            mock_catalogue=mock_catalogue,
            page_results=[
                search_result_from_publication_dataset(example_publication_dataset)
            ],
            total_results=100,
        )
        self.start_on_the_search_page()
        self.enter_a_query_and_submit("court timeliness")
        self.click_on_the_first_result()
        self.verify_i_am_on_the_publication_dataset_details_page()
        self.verify_publication_dataset_details()

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search?new=True")
        assert self.selenium.title in self.page_titles

    def click_on_the_search_button(self):
        self.search_page.search_button().click()

    def click_on_the_first_result(self):
        first_result = self.search_page.first_search_result()
        assert first_result.text

        first_link = first_result.link()
        item_name = first_link.text
        first_link.click()
        return item_name

    def verify_i_am_on_the_database_details_page(self, item_name):
        heading_text = self.details_database_page.primary_heading().text.replace(
            " Database", ""
        )
        assert heading_text == self.selenium.title.split("-")[0].strip()
        assert item_name.endswith(heading_text)

    def enter_a_query_and_submit(self, query):
        search_bar = self.search_page.search_bar()
        search_bar.send_keys(query)
        self.click_on_the_search_button()
        self.search_page.wait_for_element_to_be_visible(By.ID, "result-count")

    def verify_sort_selected(self, expected):
        value = self.search_page.checked_sort_option().get_attribute("value") or ""
        assert value == expected.lower()

    def verify_database_tables_listed(self):
        tables = self.details_database_page.database_tables()
        assert tables.text

    def verify_database_details(self):
        database_details = self.details_database_page.database_details()
        assert database_details.text

    def click_on_table(self):
        self.details_database_page.table_link().click()

    def verify_i_am_on_the_table_details_page(self, column_description):
        heading_text = self.details_database_page.primary_heading().text.replace(
            " Table", ""
        )
        assert heading_text == self.selenium.title.split("-")[0].strip()

        assert self.table_details_page.column_descriptions() == [column_description]

    def click_on_publication_collection_dataset_link(self):
        self.publication_collection_details_page.dataset_link().click()

    def verify_publication_collection_details(self):
        publication_collection_details = (
            self.publication_collection_details_page.collection_details()
        )
        assert publication_collection_details.text

    def verify_publication_dataset_details(self):
        publication_dataset_details = (
            self.publication_dataset_details_page.dataset_details()
        )
        assert publication_dataset_details.text

    def verify_publication_collection_datasets_listed(self):
        publications = self.publication_collection_details_page.datasets()
        assert publications.text

    def verify_i_am_on_the_publications_collections_details_page(self, item_name):
        heading_text = (
            self.publication_collection_details_page.primary_heading().text.replace(
                " Publication collection", ""
            )
        )
        assert heading_text == self.selenium.title.split("-")[0].strip()
        assert item_name.endswith(heading_text)

    def verify_i_am_on_the_publication_dataset_details_page(self):
        heading_text = (
            self.publication_dataset_details_page.primary_heading().text.replace(
                " Publication dataset", ""
            )
        )
        assert heading_text == self.selenium.title.split("-")[0].strip()
